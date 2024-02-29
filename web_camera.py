import time
import cv2
from flask import Flask, request, render_template, Response, send_file
from flask_cors import CORS
import base64
import numpy as np
from flask_socketio import SocketIO, emit
import pyttsx3
import multiprocessing
from p3_shoot import detect_face


def save_audio(text):
    engine = pyttsx3.init()
    engine.save_to_file(text, "output.wav")
    engine.runAndWait()


def final_realize():
    app = Flask(__name__)
    CORS(app)
    socketio = SocketIO(app)
    direction = multiprocessing.Value('i', 0)
    judge = multiprocessing.Value('b', True)
    judge2 = multiprocessing.Value('b', True)
    shoot = multiprocessing.Value('b', False)
    shoot2 = multiprocessing.Value('b', False)
    shoot3 = multiprocessing.Value('b', False)
    img = None
    image = None
    temp = time.time()
    temp2 = time.time()

    @app.route('/')
    def index():
        nonlocal temp2
        temp2 = time.time()
        judge.value = True
        judge2.value = True
        shoot.value = False
        shoot2.value = False
        shoot3.value = False
        return render_template('image.html')

    # 处理从前端传来的视频帧
    @app.route('/process_frame', methods=['GET', 'POST'])
    def process_frame():
        nonlocal img, image, temp
        if judge.value:
            # 开始四秒等待用户前端界面加载完成，然后播放开始音频
            if time.time() - temp2 > 4:
                judge.value = False
                return "announce"
        frame_data = request.get_json()
        frame = frame_data['frame']
        # 将Base64编码的图像数据解码为numpy数组
        encoded_data = frame.split(',')[1]
        np_arr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        try:
            # 将numpy数组转换为OpenCV的图像对象
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            img = cv2.flip(img, 1)
            # 等待开始音频播放完毕
            if time.time() - temp2 < 8:
                height_, width_ = img.shape[:2]
                detect_face(img, direction, width_, height_)
                image = cv2.imencode('.jpg', img)[1].tobytes()
                return "image"
            if shoot3.value:
                return ""
            if shoot2.value:
                shoot3.value = True
                return "announce"
            if not shoot.value:
                height_, width_ = img.shape[:2]
                detect_face(img, direction, width_, height_)
            else:
                shoot2.value = True
            image = cv2.imencode('.jpg', img)[1].tobytes()
            if direction.value == 0 or (time.time() - temp < 1.5):
                return "image"
            else:
                temp = time.time()
                return "announce"
        except Exception:
            return ""

    def gen():
        try:
            return (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
        except Exception:
            return ""

    @app.route('/video_feed')
    def video_feed():
        return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/audio')
    def audio():
        filename = "output.wav"  # 音频文件的路径
        if judge2.value:
            judge2.value = False
            save_audio("欢迎使用视界之声智慧拍照")
        elif shoot3.value:
            save_audio("拍照成功")
        elif direction.value == 1:
            save_audio("向左")
        elif direction.value == 2:
            save_audio("向右")
        elif direction.value == 3:
            save_audio("向上")
        elif direction.value == 4:
            save_audio("向下")
        elif direction.value == -1:
            save_audio("看不到你")
        else:
            return ""
        return send_file(filename, mimetype='audio/wav')  # 返回音频文件

    # 处理WebSocket连接和消息
    @socketio.on('message')
    def handle_message(message):
        print(message)
        nonlocal temp
        if message == "shoot":
            shoot.value = not shoot.value
            shoot2.value = False
            shoot3.value = False
            temp = time.time() + 1.5
        # 向前端发送接收到的文本消息
        emit('message', message)

    socketio.run(app, host='0.0.0.0', port=5000, log_output=True, use_reloader=True, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    final_realize()
