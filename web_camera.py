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
    wait_start = multiprocessing.Value('b', True)  # 判断是否播放欢饮音频
    welcome = multiprocessing.Value('b', True)  # 播放欢迎音频的音频选择标签
    shoot = multiprocessing.Value('b', False)  # 拍照
    success_an = multiprocessing.Value('b', False)  # 播放拍照成功音频
    shoot3 = multiprocessing.Value('b', False)  # 保持拍照后画面静止
    img = None
    temp2 = time.time()  # 页面加载等待及欢迎音频播放时长
    X, Y, W, H = 0, 0, 0, 0

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
        nonlocal temp2, X, Y, W, H
        temp2 = time.time()
        X, Y, W, H = 0, 0, 0, 0
        wait_start.value = True
        welcome.value = True
        shoot.value = False
        success_an.value = False
        return render_template('image.html')

    # 处理从前端传来的视频帧
    @app.route('/process_frame', methods=['GET', 'POST'])
    def process_frame():
        nonlocal img, X, Y, W, H
        if wait_start.value:
            # 开始四秒等待用户前端界面加载完成，然后播放开始音频
            if time.time() - temp2 > 4:
                wait_start.value = False
                return "a"
        frame_data = request.get_json()
        frame = frame_data['frame']
        # 将Base64编码的图像数据解码为numpy数组
        encoded_data = frame.split(',')[1]
        np_arr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        # 开始时，视频帧可能过段时间才向后端传递，此时会产生异常，故用try
        try:
            # 将numpy数组转换为OpenCV的图像对象
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            # 等待开始音频播放完毕
            if time.time() - temp2 < 8:
                # 播放欢迎音频时框出人脸并反馈方位
                height_, width_ = img.shape[:2]
                X, Y, W, H = detect_face(img, direction, width_, height_)
                return "i"
            if not shoot.value:
                # 常态下框出人脸并反馈方位
                height_, width_ = img.shape[:2]
                X, Y, W, H = detect_face(img, direction, width_, height_)
            else:
                return ""
            if direction.value == 0:
                return "i"
            else:
                return "a"
        except Exception:
            return ""

    # def gen():
    #     try:
    #         return (b'--frame\r\n'
    #                 b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')
    #     except Exception:
    #         return ""

    @app.route('/face_loc')
    def face_loc():
        # return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')
        return jsonify({'x': X, 'y': Y, 'w': W, 'h': H})

    @app.route('/audio')
    def audio():
        filename = "output.wav"  # 音频文件的路径
        if welcome.value:  # 判断是否播放欢迎音频
            welcome.value = False
            save_audio("欢迎使用视界之声智慧拍照")
        elif success_an.value:
            save_audio("拍照成功")
        elif direction.value == 1:
            save_audio("向右")
        elif direction.value == 2:
            save_audio("向左")
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
        if message == "shoot":
            shoot.value = not shoot.value
            success_an.value = not success_an.value
            if shoot.value:
                emit('message', 'a')
        else:
            emit('message', message)

    socketio.run(app, host='0.0.0.0', port=5000,
                 log_output=True, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    final_realize()
