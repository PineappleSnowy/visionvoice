# # import cv2
# # import multiprocessing
# #
# #
# # def read_image(queue):
# #     # 读取图片
# #     image = cv2.imread('picture.jpg')
# #     # 将图片放入队列
# #     queue.put(image)
# #
# #
# # def write_image(queue):
# #     # 从队列中获取图片
# #     image = queue.get()
# #     cv2.imshow("window", image)
# #     cv2.waitKey(0)
# #     # 写入图片
# #     cv2.imwrite('image_copy.jpg', image)
# #
# #
# # if __name__ == '__main__':
# #     # 创建队列
# #     queue = multiprocessing.Queue()
# #
# #     # 创建读取图片进程
# #     read_process = multiprocessing.Process(target=read_image, args=(queue,))
# #     read_process.start()
# #
# #     # 创建写入图片进程
# #     write_process = multiprocessing.Process(target=write_image, args=(queue,))
# #     write_process.start()
# #
# #     # 等待进程执行完成
# #     read_process.join()
# #     write_process.join()
#
# import sys
# import cv2
# from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
# from PyQt5.QtGui import QImage, QPixmap
# from PyQt5.QtCore import Qt
#
#
# class WebcamDisplay(QMainWindow):
#     def __init__(self):
#         super().__init__()
#
#         self.setWindowTitle("Webcam Display")
#
#         self.label = QLabel(self)
#         self.label.setAlignment(Qt.AlignCenter)
#         self.setCentralWidget(self.label)
#
#         self.cap = cv2.VideoCapture(0)
#
#         self.timer = self.startTimer(1)
#
#     def timerEvent(self, event):
#         ret, frame = self.cap.read()
#         if ret:
#             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
#             pixmap = QPixmap.fromImage(image)
#             self.label.setPixmap(pixmap.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio))
#
#     def closeEvent(self, event):
#         self.cap.release()
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = WebcamDisplay()
#     window.show()
#     sys.exit(app.exec_())
import cv2

# import multiprocessing
#
# import cv2
# import numpy as np
#
#
# def worker_func(arr):
#     img = cv2.imread('image_0.jpg')
#     arr[:img.shape[0] * img.shape[1] * img.shape[2]] = img.flatten()  # 将图片数据拷贝到共享内存数组中
#
#
# if __name__ == '__main__':
#     img = cv2.imread('image_0.jpg')
#     height, width, channel = img.shape
#     shared_arr = multiprocessing.Array('B', height * width * channel)  # 创建一个共享内存数组，存储图片数据
#     process = multiprocessing.Process(target=worker_func, args=(shared_arr,))
#     process.start()
#     process.join()
#
#     img = np.frombuffer(shared_arr.get_obj(), dtype=np.uint8).reshape((height, width, 3))
#     print(f"img:{img}")
#     cv2.imshow("window", img)
#     cv2.waitKey(0)

# import sys
# import cv2
# from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
# from PyQt5.QtGui import QImage, QPixmap
# from PyQt5.QtCore import Qt
# import multiprocessing
#
# height, width = 480, 640
# arr = multiprocessing.Array('B', height * width * 3)
#
# class WebcamDisplay(QMainWindow):
#     def __init__(self):
#         super().__init__()
#
#         self.setWindowTitle("Webcam Display")
#
#         self.label = QLabel(self)
#         self.label.setAlignment(Qt.AlignCenter)
#         self.setCentralWidget(self.label)
#
#         self.cap = cv2.VideoCapture(0)
#
#         self.timer = self.startTimer(1)
#
#     def timerEvent(self, event):
#         ret, frame = self.cap.read()
#         if ret:
#             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             arr[:frame.shape[0] * frame.shape[1] * frame.shape[2]] = frame.flatten()
#             image = QImage(bytes(arr), frame.shape[1], frame.shape[0], QImage.Format_RGB888)
#             pixmap = QPixmap.fromImage(image)
#             self.label.setPixmap(pixmap.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio))
#
#     def closeEvent(self, event):
#         self.cap.release()
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = WebcamDisplay()
#     window.show()
#     sys.exit(app.exec_())

img = cv2.imread("visionvoice_logo.jpg")
img = cv2.resize(img, None, fx=1000/750, fy=1000/750)
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
height, width = img.shape[:2]
threshold = 240
for i in range(height):
    for j in range(width):
        if img_gray[i, j] > 200:
            img_gray[i, j] = threshold
        else:
            img_gray[i, j] = 0
cv2.imshow("dst", img_gray)
cv2.waitKey(0)
img = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR)
cv2.imwrite("logo.jpg", img)

