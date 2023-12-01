import multiprocessing
import time
import cv2
from p3_image_analyse import final_realize_IA, faster_whisper_recognize
from p3_shoot import final_realize_shoot, voice_announce, speech_recognize_init
from pyqt_UI import qt_process


value_ = multiprocessing.Value("i", 0)


def final_main():
    choose1 = "智慧拍照"
    choose2 = "环境识别"
    choose3 = "退出"
    r = speech_recognize_init()
    image = cv2.imread("image_data/picture2.jpg")
    cv2.imwrite("image_data/picture.jpg", image)
    qt_process(value_)
    time.sleep(4)
    voice_announce(f"欢迎使用视界之声，请选择你的服务。1、{choose1}。2、{choose2}")
    while True:
        print(value_.value)
        if value_.value == 3:
            voice_announce("退出成功")
            return 0
        elif value_.value == 2:
            final_realize_IA()
            voice_announce(f"您可以说退出以退出程序，或者继续选择服务。1、{choose1}。2、{choose2}")
        elif value_.value == 1:
            final_realize_shoot()
            voice_announce(f"您可以说退出以退出程序，或者继续选择服务。1、{choose1}。2、{choose2}")
        value_.value = 0
        image = cv2.imread("image_data/picture2.jpg")
        cv2.imwrite("image_data/picture.jpg", image)
        segments = faster_whisper_recognize("output.wav", r, choose1 + choose2 + choose3)
        for segment in segments:
            print(f"text: {segment.text}")
            if choose3 in segment.text:
                value_.value = 3
                voice_announce("退出成功")
                return 0
            elif choose2 in segment.text:
                value_.value = 2
                break
            elif choose1 in segment.text:
                value_.value = 1
                break


if __name__ == "__main__":
    final_main()
