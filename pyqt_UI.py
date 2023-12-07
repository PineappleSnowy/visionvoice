import multiprocessing
import os
import threading
import time
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QProgressBar, QTextEdit


class MyWindow(QMainWindow):
    def __init__(self, func1, name1, func2, name2, func3, name3, windowTitle,
                 answer_value_, key_value_):
        super().__init__()
        self.answer = answer_value_
        self.key = key_value_
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
        self.button1.setFocusPolicy(Qt.NoFocus)

        self.button2 = QPushButton(name2, self)
        self.button2.setGeometry(50, 400, 300, 200)
        self.button2.clicked.connect(func2)
        self.button2.setStyleSheet("background-color: orange;")
        self.button2.setFont(font)
        self.button2.setFocusPolicy(Qt.NoFocus)

        self.button3 = QPushButton(name3, self)
        self.button3.setGeometry(50, 700, 300, 200)
        self.button3.clicked.connect(func3)
        self.button3.setStyleSheet("background-color: orange;")
        self.button3.setFont(font)
        self.button3.setFocusPolicy(Qt.NoFocus)

        # 创建文本框控件
        self.text_edit = QTextEdit(self)
        self.text_edit.setGeometry(400, 850, 1550, 300)  # 设置文本框的位置和大小
        font = QFont()
        font.setPointSize(16)
        self.text_edit.setFont(font)
        self.text_edit.setPlainText(self.answer.value)  # 填入多行文本
        self.text_edit.setFocusPolicy(Qt.NoFocus)

        # 设置窗口属性
        self.setGeometry(260, 100, 2000, 1200)
        self.setWindowTitle(windowTitle)

    def update_frame(self):
        self.pixmap = QPixmap("image_data/picture.jpg")
        self.label.setPixmap(self.pixmap)
        self.text_edit.setPlainText(self.answer.value)

    def keyPressEvent(self, event):
        print(event.key())
        # 按下"esc"键强制终止程序
        if event.key() == Qt.Key_Escape:
            os.system("taskkill /F /IM python.exe")
        # 按下空格改变判断标识
        elif event.key() == Qt.Key_Space:
            self.key.value = True


def qt_process(value, answer_value_, key_value_):
    qt_process_ = multiprocessing.Process(target=qt_exec,
                                          args=(value, answer_value_, key_value_),
                                          daemon=True)
    qt_process_.start()


def qt_exec(value, answer_value_, key_value_):
    def func1():
        value.value = 1

    def func2():
        value.value = 2

    def func3():
        value.value = 3

    app = QApplication([])
    window = MyWindow(func1, "智慧拍照", func2, "环境识别", func3, "退出", "视界之声",
                      answer_value_, key_value_)
    window.show()
    timer = QTimer()
    timer.timeout.connect(window.update_frame)
    timer.start(30)
    app.exec_()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("视界之声正在加载...")
        self.setGeometry(260, 100, 2000, 1200)

        self.load_label = QLabel(self)

        self.label = QLabel(self)
        self.image = QPixmap("image_data/dst_start_img.png")
        self.label.resize(self.image.width(), self.image.height())
        self.label.setPixmap(self.image)
        self.label.move(500, 100)

        self.dream_label = QLabel("   希望不再有于黑暗中踽踽独行者\n每一个灵魂都拥有拥抱光彩世界的自由", self)
        font = QFont()
        font.setPointSize(20)
        self.dream_label.setFont(font)
        self.dream_label.setGeometry(660, 650, 800, 100)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(250, 800, 1500, 50)

        self.tip_label = QLabel('视界之声快捷键：\n1、按"esc"键中止程序\n2、按空格键拍照或立即开始识别环境', self)
        font = QFont()
        font.setPointSize(16)
        self.tip_label.setFont(font)
        self.tip_label.setGeometry(745, 850, 600, 150)
        color = QColor(185, 0, 0)
        self.tip_label.setStyleSheet("color: %s;" % color.name())

        self.text_label = QLabel(self)
        self.text_label.setText("登录visionvoice官网了解我们的更多信息。\nhttps://visionvoice.geek-tech.group/")
        font = QFont()
        font.setPointSize(15)
        self.text_label.setFont(font)
        self.text_label.setGeometry(725, 1050, 600, 100)

    def update_progress(self):
        value = self.progress_bar.value() + 1
        if value > 100:
            time.sleep(1)
            self.close()
        if value == 100:
            self.load_label.setGeometry(1800, 800, 250, 50)
            self.load_label.setText("加载完成！")
            font = QFont()
            font.setPointSize(14)
            self.load_label.setFont(font)
            color = QColor(0, 135, 0)
            self.load_label.setStyleSheet("color: %s;" % color.name())
        self.progress_bar.setValue(value)

    def keyPressEvent(self, event):
        # 按下"esc"键强制终止程序
        if event.key() == Qt.Key_Escape:
            os.system("taskkill /F /IM python.exe")


def start_exec(value):
    app_ = QApplication([])
    window_ = MainWindow()
    window_.show()
    timer = QTimer()
    timer.timeout.connect(window_.update_progress)
    timer.start(95)
    app_.exec_()
    value.value = 0


def start_thread(value):
    start_thread_ = threading.Thread(target=start_exec, args=(value,))
    start_thread_.start()


if __name__ == "__main__":
    pass
