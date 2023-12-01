import multiprocessing
import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QFont
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel


class MyWindow(QMainWindow):

    def update_frame(self):
        self.pixmap = QPixmap("image_data/picture.jpg")
        self.label.setPixmap(self.pixmap)

    def __init__(self, func1, name1, func2, name2, func3, name3, windowTitle):
        super().__init__()
        self.label = QLabel(self)
        self.pixmap = QPixmap("image_data/picture.jpg")
        self.label.setPixmap(self.pixmap)
        self.label.resize(self.pixmap.width(), self.pixmap.height())
        self.label.move(700, 300)

        font = QFont()
        font.setPointSize(16)
        # 创建按钮
        self.button1 = QPushButton(name1, self)
        self.button1.setGeometry(50, 100, 300, 200)
        self.button1.clicked.connect(func1)
        self.button1.setStyleSheet("background-color: orange;")
        self.button1.setFont(font)

        self.button2 = QPushButton(name2, self)
        self.button2.setGeometry(50, 400, 300, 200)
        self.button2.clicked.connect(func2)
        self.button2.setStyleSheet("background-color: orange;")
        self.button2.setFont(font)

        self.button3 = QPushButton(name3, self)
        self.button3.setGeometry(50, 700, 300, 200)
        self.button3.clicked.connect(func3)
        self.button3.setStyleSheet("background-color: orange;")
        self.button3.setFont(font)
        # 设置窗口属性
        self.setGeometry(260, 50, 2000, 1200)
        self.setWindowTitle(windowTitle)


def qt_process(value):
    qt_process_ = multiprocessing.Process(target=qt_exec,
                                          args=(value,),
                                          daemon=True)
    qt_process_.start()


def qt_exec(value):
    def func1():
        value.value = 1

    def func2():
        value.value = 2

    def func3():
        value.value = 3

    app = QApplication(sys.argv)
    window = MyWindow(func1, "智慧拍照", func2, "环境识别", func3, "退出", "视界之声")
    window.show()
    timer = QTimer()
    timer.timeout.connect(window.update_frame)
    timer.start(30)
    app.exec_()


if __name__ == "__main__":
    image = cv2.imread("image_data/picture2.jpg")
    image2 = cv2.imread("image_data/picture.jpg")
    height, width, channel = image2.shape
    image = cv2.resize(image, (int(width), int(height)))
    cv2.imwrite("image_data/picture2.jpg", image)
