import multiprocessing
import threading
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QProgressBar


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

    app = QApplication([])
    window = MyWindow(func1, "智慧拍照", func2, "环境识别", func3, "退出", "视界之声")
    window.show()
    timer = QTimer()
    timer.timeout.connect(window.update_frame)
    timer.start(30)
    app.exec_()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("视界之声正在加载...")
        self.setGeometry(260, 50, 2000, 1200)

        self.label = QLabel(self)
        self.image = QPixmap("dst_start_img.png")
        self.label.resize(self.image.width(), self.image.height())
        self.label.setPixmap(self.image)
        self.label.move(500, 100)
        self.label.setScaledContents(True)

        self.dream_label = QLabel("   希望不再有于黑暗中踽踽独行者\n每一个灵魂都拥有拥抱光彩世界的自由", self)
        font = QFont()
        font.setPointSize(20)
        self.dream_label.setFont(font)
        self.dream_label.setGeometry(660, 750, 800, 100)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(250, 900, 1500, 50)

        self.text_label = QLabel(self)
        self.text_label.setText("登录visionvoice官网了解我们的更多信息。\nhttps://visionvoice.geek-tech.group/")
        font = QFont()
        font.setPointSize(15)
        self.text_label.setFont(font)
        self.text_label.setGeometry(725, 1050, 600, 100)

    def update_progress(self):
        value = self.progress_bar.value() + 1
        if value >= 100:
            self.close()
        self.progress_bar.setValue(value)


def start_exec():
    app_ = QApplication([])
    window_ = MainWindow()
    window_.show()
    timer = QTimer()
    timer.timeout.connect(window_.update_progress)
    timer.start(70)
    app_.exec_()


def start_thread():
    start_thread_ = threading.Thread(target=start_exec)
    start_thread_.start()


start_thread()


if __name__ == "__main__":
    pass
