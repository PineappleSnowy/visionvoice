import time
import cv2
from flask import Flask, request, render_template, Response, send_file, jsonify
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
    # CORS解决跨域访问问题
    CORS(app)
    socketio = SocketIO(app)
    direction = multiprocessing.Value('i', 0)  # 人脸位置标签
    judge = multiprocessing.Value('b', True)  # 判断是否播放欢饮音频
    judge2 = multiprocessing.Value('b', True)  # 播放欢迎音频的音频选择标签
    shoot = multiprocessing.Value('b', False)  # 拍照
    shoot2 = multiprocessing.Value('b', False)  # 播放拍照成功音频
    shoot3 = multiprocessing.Value('b', False)  # 保持拍照后画面静止
    img = None
    image = None
    temp = time.time()  # 方向提示音频播放时长
    temp2 = time.time()  # 页面加载等待及欢迎音频播放时长
    X , Y, W, H = 0, 0, 0, 0

    # @app.after_request
    # def add_header(response):
    #     response.headers['Access-Control-Allow-Origin'] = '*'  # 允许所有域名跨域访问
    #     response.headers['Access-Control-Allow-Headers'] = 'Content-Type'  # 允许的请求头
    #     response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'  # 允许的HTTP方法
    #
    #     return response

    @app.route('/')
    def index():
        # 初始化参数信息
        nonlocal temp2, X , Y, W, H
        temp2 = time.time()
        X , Y, w, h = 0, 0, 0, 0
        judge.value = True
        judge2.value = True
        shoot.value = False
        shoot2.value = False
        shoot3.value = False
        return render_template('image.html')

    # 处理从前端传来的视频帧
    @app.route('/process_frame', methods=['GET', 'POST'])
    def process_frame():
        nonlocal img, image, temp, X , Y, W, H
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
        # 开始时，视频帧可能过段时间才向后端传递，此时会产生异常，故用try
        try:
            # 将numpy数组转换为OpenCV的图像对象
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            # img = cv2.flip(img, 1)
            # 等待开始音频播放完毕
            if time.time() - temp2 < 8:
                # 播放欢迎音频时框出人脸并反馈方位
                height_, width_ = img.shape[:2]
                X , Y, W, H = detect_face(img, direction, width_, height_)
                image = cv2.imencode('.jpg', img)[1].tobytes()
                return "image"
            if shoot3.value:
                # 保持画面静止
                return ""
            if shoot2.value:
                # 播放拍照成功
                shoot3.value = True
                return "announce"
            if not shoot.value:
                # 常态下框出人脸并反馈方位
                height_, width_ = img.shape[:2]
                X , Y, W, H = detect_face(img, direction, width_, height_)
            else:
                # 此时shoot==True，拍照，不画人脸框
                shoot2.value = True
            image = cv2.imencode('.jpg', img)[1].tobytes()
            # 1.5秒等待方向音频播放完毕
            if direction.value == 0 or (time.time() - temp < 1.5):
                return "image"
            else:
                # 更新时间
                temp = time.time()
                return "announce"
        except Exception:
            return ""

    def gen():
        # 处理image仍为None的异常
        try:
            return (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
        except Exception:
            return ""

    @app.route('/video_feed')
    def video_feed():
        # 访问gen()函数，返回图片字节信息
        # return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')
        return jsonify({'x': X, 'y': Y, 'w': W, 'h': H})

    @app.route('/audio')
    def audio():
        filename = "output.wav"  # 音频文件的路径
        if judge2.value:  # 判断是否播放欢迎音频
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
        # message内容包括后端路由文本返回值以及前端发来的文本消息
        nonlocal temp
        if message == "shoot":
            # 前端发来拍照或再拍一张的指令，修改一系列参量
            shoot.value = not shoot.value
            # 以下两个参数修改为再拍一张服务，对拍照指令不影响
            shoot2.value = False
            shoot3.value = False
            # 给拍照成功的语音播报提供更多时间
            temp = time.time() + 1.5
        # 向前端发送接收到的文本消息
        emit('message', message)

    socketio.run(app, host='0.0.0.0', port=5000, log_output=True, use_reloader=True, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    final_realize()
