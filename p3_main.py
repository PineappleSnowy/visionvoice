from p3_image_analyse import final_realize_IA, faster_whisper_recognize
from p3_shoot import final_realize_shoot, voice_announce, speech_recognize_init


def final_main():
    choose1 = "智慧拍照"
    choose2 = "环境识别"
    choose3 = "退出"
    r = speech_recognize_init()
    voice_announce(f"欢迎使用智慧盲人相机，请选择你的服务。1、{choose1}。2、{choose2}")
    while True:
        segments = faster_whisper_recognize("output.wav", choose1 + choose2 + choose3)
        for segment in segments:
            print(f"text: {segment.text}")
            if choose1 in segment.text:
                final_realize_shoot(r)
                voice_announce(f"您可以说退出以退出程序，或者继续选择服务。1、{choose1}。2、{choose2}")
                break
            elif choose2 in segment.text:
                final_realize_IA()
                voice_announce("您可以说退出以退出程序，或者继续选择服务")
                break
            elif choose3 in segment.text:
                voice_announce("退出成功")
                return 0


if __name__ == "__main__":
    final_main()
