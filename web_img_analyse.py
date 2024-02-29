import multiprocessing
import time
import cv2
from flask import Flask, request, render_template, send_file
from flask_cors import CORS
import base64
import numpy as np
from flask_socketio import SocketIO, emit
import ctypes
from p3_ImageUnderstanding import spark_chat, image_understanding
import pyttsx3

temp = time.time()
restart = False
model_process = multiprocessing.Process()
model_process2 = multiprocessing.Process()
max_img_num = 3


def analyse_img_process(flag_, img_data_list_, scene_value_, answer_value_):
    while True:
        if flag_.value > max_img_num:
            break
    spark_chat(img_data_list_, scene_value_, answer_value_)
    save_audio(answer_value_.value)
    flag_.value = max_img_num + 2


def save_audio(text):
    engine = pyttsx3.init()
    engine.save_to_file(text, "output.wav")
    engine.runAndWait()


def final_realize():
    global model_process, model_process2
    app = Flask(__name__)
    CORS(app)
    socketio = SocketIO(app)
    flag = multiprocessing.Value('i', 0)
    img_data_list = multiprocessing.Manager().list([])
    scene_value = multiprocessing.Manager().Value(ctypes.c_char_p, "indoor")
    answer_value = multiprocessing.Manager().Value(ctypes.c_char_p, "")

    model_process = multiprocessing.Process(target=analyse_img_process,
                                            args=(flag, img_data_list, scene_value, answer_value))
    model_process2 = multiprocessing.Process(target=analyse_img_process,
                                             args=(flag, img_data_list, scene_value, answer_value))

    def temp_process():
        model_process.start()

    def init():
        global restart, temp, model_process, model_process2
        restart = False
        temp = time.time()
        flag.value = 0
        if model_process.is_alive():
            model_process.terminate()
            model_process2 = multiprocessing.Process(target=analyse_img_process,
                                                     args=(flag, img_data_list, scene_value, answer_value))
            model_process2.start()
        elif model_process2.is_alive():
            model_process2.terminate()
            model_process = multiprocessing.Process(target=analyse_img_process,
                                                    args=(flag, img_data_list, scene_value, answer_value))
            model_process.start()
        else:
            model_process = multiprocessing.Process(target=analyse_img_process,
                                                    args=(flag, img_data_list, scene_value, answer_value))
            model_process.start()
        flag.value = 0
        answer_value.value = ""
        img_data_list[:] = []

    @app.route('/')
    def route_():
        init()
        return render_template("index.html")

    @app.route('/audio')
    def audio():
        filename = "output.wav"  # 音频文件的路径
        return send_file(filename, mimetype='audio/wav')  # 返回音频文件

    # 处理从前端传来的视频帧
    @app.route('/process_frame', methods=['GET', 'POST'])
    def process_frame():
        if restart:
            init()
        if time.time() - temp > 2:
            if flag.value == 0:
                flag.value = 1
                save_audio(
                    "欢迎使用视界之声环境识别。听到录像开始后请缓慢地转动镜头，总时长15秒，"
                    "我将根据镜头画面识别当前环境。当画面重复时我会自动停止。录像开始")
                return "output"
        if not time.time() - temp > 18:
            return "视界之声的回答：\n  "
        else:
            frame_data = request.get_json()
            frame = frame_data['frame']
            # 将Base64编码的图像数据解码为numpy数组
            encoded_data = frame.split(',')[1]
            np_arr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
            if flag.value <= max_img_num:
                try:
                    # 将numpy数组转换为OpenCV的图像对象
                    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                    img_data_list.extend(image_understanding(img))
                    flag.value = min(flag.value + 1, max_img_num + 1)
                except Exception:
                    pass
                return "视界之声的回答：\n  "
            # 正在进行最终环境识别
            elif flag.value == max_img_num + 1:
                return "视界之声的回答：\n  " + answer_value.value
            # 最终环境识别结束，显示最终结果
            elif flag.value == max_img_num + 2:
                flag.value += 1
                return "视界之声的回答：\n  " + answer_value.value
            # 进入语音播报阶段
            elif flag.value == max_img_num + 3:
                flag.value = max_img_num + 4
                return "output"
            else:
                return "视界之声的回答：\n  " + answer_value.value
        print("erro********************")
        return ""

    # 处理WebSocket连接和消息
    @socketio.on('message')
    def handle_message(message):
        global restart
        if message == 'Restarted!':
            print("restarted###########")
            restart = True
        # 向前端发送接收到的文本消息
        emit('message', message)

    temp_process()
    socketio.run(app, host='0.0.0.0', port=5000, log_output=True, use_reloader=True, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    final_realize()
