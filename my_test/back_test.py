from flask import Flask, jsonify, render_template
import random

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('test.html')


@app.route('/getRandomPosition')
def get_random_position():
    x = random.randint(0, 350)  # Random x position within canvas
    y = random.randint(0, 250)  # Random y position within canvas
    return jsonify({'x': x, 'y': y})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
# import pyttsx3
#
# engine = pyttsx3.init()
# text = "视界之声介绍\n"
# "背景\n"
# "盲人作为世界上的弱势群体，独立认识环境一直是个大问题，传统导盲犬无法传递复杂的环境信息，最新的google盲人眼镜则价格不菲。如何给盲人提供一个低门槛且有效的感知环境的方式，是视界之声探索的话题。"
# "核心技术\n"
# "我们的产品的核心技术包括基于ResNet18的场景分类模型、基于ORB算法的特征点检测、基于mediapipe的人脸检测、基于faster-whisper的语音识别、基于pyttsx3的语音合成以及多种大模型调用。"
# "产品功能\n"
# "产品分为PC端和Android端，可全语音控制。视界之声包括两个主功能：环境识别和智慧拍照。"
# "环境识别：产品通过用户设备摄像头获取四周环境信息，整合后调用模型和函数，反馈出对环境信息的自然语言描述，并合成语音播报。"
# "智慧拍照：产品检测人脸在画面中的位置，通过实时语音引导用户调整面部至画面中心，之后可声控拍照。产品可处理多人脸同时出现情况。拍照之后调用大模型从光线、内容、色彩等角度对照片进行评价，让盲人也能拍出好看的照片。"
# "对AI开源的贡献\n"
# "我们注册了域名和公网IP，建立了自己的网页，允许全世界的用户体验产品并与我们联系。项目的部分代码在社区github与swanhub上开源，助力中国AI开源生态！"
# "我们的团队\n"
# "西安电子科技大学PineappleSnowy团队，"
# "一支由00后组成的科技创新队伍"
# engine.save_to_file(text, "output.mp3")
# engine.runAndWait()
