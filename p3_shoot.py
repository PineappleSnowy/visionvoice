import cv2
import mediapipe as mp
import multiprocessing

judge_shoot = multiprocessing.Value('b', False)
judge_announce = False
direction = 0
window_name = "Face Detection"
detect_sign = 0
const_face_list = []
width_, height_ = [0, 0]


def detect_face(img, direct_value, w, h):
    direct_value.value = 0
    # 加载模型
    face_detector = mp.solutions.face_detection.FaceDetection(
        min_detection_confidence=0.4, model_selection=0)
    # mp_drawing = mp.solutions.drawing_utils（可选，与draw_detection配套使用）
    # 将读取到的图片由BGR转换成RGB，并传入模型
    results = face_detector.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 遍历检测到的人脸并绘制矩形框
    if results.detections:
        if len(results.detections) > 1:
            for face in results.detections:
                box = face.location_data.relative_bounding_box
                xmin, ymin, width, height = [
                    box.xmin, box.ymin, box.width, box.height]
                cv2.rectangle(img, (int(xmin * w), int(ymin * h)),
                              (int((xmin + width) * w), int((ymin + height) * h)),
                              (255, 255, 255), 1)
                # const_face_list.append([xmin, ymin, width, height])
            face_list = list(results.detections)
            face_list.sort(key=lambda x: x.location_data.relative_bounding_box.width,
                           reverse=True)
            face_main = face_list[0]
        else:
            face_main = results.detections[0]
        box = face_main.location_data.relative_bounding_box
        xmin, ymin, width, height = [box.xmin, box.ymin, box.width, box.height]
        if xmin + width / 2 <= 0.3:
            direct_value.value = 1
        elif xmin + width / 2 >= 0.7:
            direct_value.value = 2
        elif ymin + height / 2 <= 0.3:
            direct_value.value = 3
        elif ymin + height / 2 >= 0.7:
            direct_value.value = 4
        # const_face_list.append([xmin, ymin, width, height])
        # 这里如果用mp_drawing.draw_detection(img, face)可绘制面部关键点
        cv2.rectangle(img, (int(xmin * w), int(ymin * h)),
                      (int((xmin + width) * w), int((ymin + height) * h)),
                      (0, 255, 0), 2)
        return int(2 * xmin * w), int(2 * ymin * h), int(2 * width * w), int(2 * height * h)
    else:
        direct_value.value = -1
        return 0, 0, 0, 0


def draw_const_face(img):
    if const_face_list:
        for face in const_face_list[:-1:]:
            xmin, ymin, width, height = face
            cv2.rectangle(img, (int(xmin * width_), int(ymin * height_)),
                          (int((xmin + width) * width_),
                           int((ymin + height) * height_)),
                          (255, 255, 255), 1)
        xmin, ymin, width, height = const_face_list[-1]
        cv2.rectangle(img, (int(xmin * width_), int(ymin * height_)),
                      (int((xmin + width) * width_),
                       int((ymin + height) * height_)),
                      (0, 255, 0), 2)
