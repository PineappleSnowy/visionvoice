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

app = Flask(__name__)

# 初始化时间标志参量
temp = time.time()
restart = False
model_process = multiprocessing.Process()
model_process2 = multiprocessing.Process()
# 添加到环境识别的最大图片数量
max_img_num = 2


def analyse_img_process(flag_, img_data_list_, scene_value_, answer_value_):
    while True:
        # 图片数量达到最大，开始环境识别最终阶段
        if flag_.value > max_img_num:
            break
    spark_chat(img_data_list_, scene_value_, answer_value_)
    # 保存回答音频
    save_audio(answer_value_.value)
    # 更新flag状态标志
    flag_.value = max_img_num + 2


def save_audio(text):
    engine = pyttsx3.init()
    engine.save_to_file(text, "output.wav")
    engine.runAndWait()


def final_realize():
    global model_process, model_process2
    # CORS解决跨域访问问题
    CORS(app)
    socketio = SocketIO(app)
    flag = multiprocessing.Value('i', 0)  # 状态标志
    img_data_list = multiprocessing.Manager().list([])  # 图片信息列表
    scene_value = multiprocessing.Manager().Value(ctypes.c_char_p, "indoor")  # 场景分类
    answer_value = multiprocessing.Manager().Value(ctypes.c_char_p, "")  # 回答
    # 这里定义了两个环境识别的进程，用于处理用户重新开始时的进程中止缓慢问题
    model_process = multiprocessing.Process(target=analyse_img_process,
                                            args=(flag, img_data_list, scene_value, answer_value))
    model_process2 = multiprocessing.Process(target=analyse_img_process,
                                             args=(flag, img_data_list, scene_value, answer_value))

    # 初始化各种参数并刷新进程
    def init():
        global restart, temp, model_process, model_process2
        # 更新restart标志，避免重复初始化
        restart = False
        # 更新temp时间标志，开始播报欢迎语音
        temp = time.time()
        # 初始化flag，避免函数访问正在中止的进程
        flag.value = 0
        # 两个进程交替开始与中止
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
        # 再次初始化flag，避免进程中止缓慢篡改flag的value值
        flag.value = 0
        answer_value.value = ""
        img_data_list[:] = []

    @app.route('/')
    def route_():
        # 每次访问根网页时都进行一次初始化
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
            init()  # 重新开始
        # 2秒钟等待网页加载，然后播放欢迎音频
        if time.time() - temp > 2:
            if flag.value == 0:
                # 这里不使用+=是为了避免多次请求同时访问flag内存值时，其值不正常
                flag.value = 1
                save_audio(
                    "欢迎使用视界之声环境识别。听到录像开始后请缓慢地转动镜头，总时长15秒，"
                    "我将根据镜头画面识别当前环境。当画面重复时我会自动停止。录像开始")
                # output会发送给前端，使前端向后端请求音频
                return "audio_s"
        # 18秒等待欢饮音频播放完毕
        if not time.time() - temp > 18:
            return ""
        else:
            frame_data = request.get_json()
            frame = frame_data['frame']
            # 将Base64编码的图像数据解码为numpy数组
            encoded_data = frame.split(',')[1]
            np_arr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
            # 对图片进行环境识别并更新flag状态标志值
            if flag.value <= max_img_num:
                try:
                    # 将numpy数组转换为OpenCV的图像对象
                    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                    img_data_list.extend(image_understanding(img))
                    # 为避免多次访问使flag值不正常，使用min函数
                    flag.value = min(flag.value + 1, max_img_num + 1)
                except Exception:
                    pass
                return "视界之声的回答：\n  "
            # 正在进行最终环境识别，显示实时结果
            elif flag.value == max_img_num + 1:
                return "视界之声的回答：\n  " + answer_value.value
            # 最终环境识别结束，显示最终结果
            elif flag.value == max_img_num + 2:
                flag.value += 1
                return "视界之声的回答：\n  " + answer_value.value
            # 进入语音播报阶段
            elif flag.value == max_img_num + 3:
                flag.value = max_img_num + 4
                return "audio_a"
            else:
                return "视界之声的回答：\n  " + answer_value.value
        # 异常时可能会运行到这里
        print("erro********************")
        # 避免"no valid return"错误
        return ""

    # 处理WebSocket连接和消息
    @socketio.on('message')
    def handle_message(message):
        global restart
        if message == 'Restarted!':
            # 重新开始
            print("restarted###########")
            restart = True
        # 向前端发送接收到的文本消息
        emit('message', message)

    socketio.run(app, host='0.0.0.0', port=443,
                 log_output=True, allow_unsafe_werkzeug=True, ssl_context=(r"C:\Users\14704\Downloads\ssl_cert\pineapplesnowy.chat\pineapplesnowy.chat.pem", r"C:\Users\14704\Downloads\ssl_cert\pineapplesnowy.chat\pineapplesnowy.chat.key"))


if __name__ == '__main__':
    final_realize()
