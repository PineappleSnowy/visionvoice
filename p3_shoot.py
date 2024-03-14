import cv2
import mediapipe as mp


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
        return int(2 * xmin * w), int(2 * ymin * h), int(2 * width * w), int(2 * height * h)
    else:
        direct_value.value = -1
        return 0, 0, 0, 0
