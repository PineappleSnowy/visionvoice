def final_main():
    import ctypes
    import multiprocessing

    # 用于在不同进程间传递用户选择
    value_ = multiprocessing.Value('i', -1)
    answer_value = multiprocessing.Manager().Value(ctypes.c_char_p, "以下是视界之声对照片或您所处环境的描述：\n    ")
    key_value = multiprocessing.Value('b', False)

    from pyqt_UI import start_thread, qt_process

    start_thread(value_)

    import cv2
    from p3_image_analyse import final_realize_IA, faster_whisper_recognize
    from p3_shoot import final_realize_shoot, voice_announce, speech_recognize_init

    choose1 = "智慧拍照"
    choose2 = "环境识别"
    choose3 = "退出"
    # 适应噪声
    r = speech_recognize_init()
    # 初始化UI图片
    image = cv2.imread("image_data/picture2.jpg")
    cv2.imwrite("image_data/picture.jpg", image)
    # 等待噪声适应完毕
    while True:
        if value_.value == 0:
            # 启动UI进程
            qt_process(value_, answer_value, key_value)
            break
    voice_announce(f"欢迎使用视界之声，请选择您的服务。1、{choose1}。2、{choose2}")
    while True:
        print(value_.value)
        # 退出
        if value_.value == 3:
            voice_announce("退出成功")
            return 0
        # 环境识别
        elif value_.value == 2:
            final_realize_IA(answer_value, key_value)
            voice_announce(f"您可以说退出以退出程序，或者继续选择服务。1、{choose1}。2、{choose2}")
        # 智慧拍照
        elif value_.value == 1:
            final_realize_shoot(answer_value, key_value)
            voice_announce(f"您可以说退出以退出程序，或者继续选择服务。1、{choose1}。2、{choose2}")
        # 初始化value
        value_.value = 0
        # 初始化UI图片
        image = cv2.imread("image_data/picture2.jpg")
        cv2.imwrite("image_data/picture.jpg", image)
        # 语音识别
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

    """
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Keyboard Listener')
        self.setGeometry(300, 300, 250, 150)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_A:
            print('You pressed the "A" key')

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_A:
            print('You released the "A" key')

if __name__ == '__main__':
    app = QApplication([])
    widget = MyWidget()
    widget.show()
    app.exec_()
    """
