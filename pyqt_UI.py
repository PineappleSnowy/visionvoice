import multiprocessing
import threading
import time
import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel


def qt_process(func1, name1, func2, name2, func3, name3, windowTitle):
    qt_process_ = multiprocessing.Process(target=qt_exec, args=(func1, name1, func2, name2, func3, name3, windowTitle),
                                          daemon=True)
    qt_process_.start()


def qt_exec(func1, name1, func2, name2, func3, name3, windowTitle):
    app = QApplication(sys.argv)
    window = MyWindow(func1, name1, func2, name2, func3, name3, windowTitle)
    window.show()
    app.exec_()


class MyWindow(QMainWindow):
    def __init__(self, func1, name1, func2, name2, func3, name3, windowTitle):
        super().__init__()
        self.label = QLabel(self)
        pixmap = QPixmap("image_data/image_0.jpg")
        self.label.setPixmap(pixmap)
        self.label.resize(pixmap.width(), pixmap.height())
        self.label.move(700, 300)
        # 创建按钮
        self.button1 = QPushButton(name1, self)
        self.button1.setGeometry(50, 100, 300, 200)
        self.button1.clicked.connect(func1)

        self.button2 = QPushButton(name2, self)
        self.button2.setGeometry(50, 400, 300, 200)
        self.button2.clicked.connect(func2)

        self.button3 = QPushButton(name3, self)
        self.button3.setGeometry(50, 700, 300, 200)
        self.button3.clicked.connect(func3)

        # 设置窗口属性
        self.setGeometry(260, 50, 2000, 1200)
        self.setWindowTitle(windowTitle)


if __name__ == "__main__":
    pass

# app = QApplication(sys.argv)
# label = QLabel()
# label.setWindowTitle("实时显示图片")
# label.setFixedSize(640, 480)

# def update_frame():
#     ret, frame = cap.read()
#     if ret:
#         rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         h, w, ch = rgb_image.shape
#         bytes_per_line = ch * w
#         image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
#         pixmap = QPixmap.fromImage(image)
#         label.setPixmap(pixmap)
#         label.setScaledContents(True)
#
#
# cap = cv2.VideoCapture(0)
# timer = QTimer()
# timer.timeout.connect(update_frame)
# timer.start(30)
# label.show()
# sys.exit(app.exec_())
