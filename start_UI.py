# import tkinter as tk
# from tkinter import ttk
# import threading
#
#
# class MainWindow(tk.Tk):
#     def __init__(self):
#         super().__init__()
#
#         self.title("视界之声正在加载...")
#         self.geometry("1300x700+200+100")
#
#         self.label = tk.Label(self)
#         self.label.place(x=500, y=50)
#         self.image = tk.PhotoImage(file="dst_start_img.png")
#         self.label.config(image=self.image)
#         self.label.pack()
#
#         self.dream_label = tk.Label(self,
#                                     text="   希望不再有于黑暗中踽踽独行者\n每一个灵魂都拥有拥抱光彩世界的自由",
#                                     font=("Arial", 20))
#         self.dream_label.pack()
#
#         self.progress_bar = ttk.Progressbar(self, length=800)
#         self.progress_bar.pack()
#
#         self.text_label = tk.Label(self,
#                                    text="登录visionvoice官网了解我们的更多信息。\nhttps://visionvoice.geek-tech.group/",
#                                    font=("Arial", 13))
#         self.text_label.pack()
#
#         self.after(70, self.update_progress)  # 每70毫秒触发一次update_progress方法，进度条每过0.07秒加一
#
#     def update_progress(self):
#         value = self.progress_bar["value"] + 1
#         if value > 100:
#             self.quit()
#         else:
#             self.progress_bar["value"] = value
#             self.after(70, self.update_progress)
#
#
# def start_an():
#     window = MainWindow()
#     window.mainloop()
#
#
# def start_an_thread():
#     start_thread = threading.Thread(target=start_an)
#     start_thread.start()
#
#
# start_an_thread()


import sys
import threading

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QProgressBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("视界之声正在加载...")
        self.setGeometry(260, 50, 2000, 1200)

        self.label = QLabel(self)
        self.image = QPixmap("image_data/dst_start_img.png")
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
        self.text_label.setGeometry(723, 1050, 600, 100)

    def update_progress(self):
        value = self.progress_bar.value() + 1
        if value >= 100:
            self.close()
        self.progress_bar.setValue(value)


def start_exec():
    app_ = QApplication(sys.argv)
    window_ = MainWindow()
    window_.show()
    timer = QTimer()
    timer.timeout.connect(window_.update_progress)
    timer.start(70)
    app_.exec_()


def start_thread():
    start_thread_ = threading.Thread(target=start_exec)
    start_thread_.start()


if __name__ == "__main__":
    start_thread()
