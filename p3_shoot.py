import cv2
import mediapipe as mp
import speech_recognition as sr
import pyttsx3
import threading
from faster_whisper import WhisperModel
import time
import multiprocessing
from p3_ImageUnderstanding import image_understanding, voice_announce_thread

judge_shoot = multiprocessing.Value('b', False)
judge_announce = False
direction = 0
window_name = "Face Detection"
detect_sign = 0
const_face_list = []
width_, height_ = [0, 0]
r = sr.Recognizer()


def speech_recognize_init():
    r.non_speaking_duration = 0.1
    r.pause_threshold = 0.1
    with sr.Microphone() as mic:
        r.adjust_for_ambient_noise(mic, duration=1)
    return r


def detect_face(img):
    global direction
    global detect_sign

    # 加载模型
    face_detector = mp.solutions.face_detection.FaceDetection(min_detection_confidence=0.4, model_selection=0)
    # mp_drawing = mp.solutions.drawing_utils（可选，与draw_detection配套使用）
    # 将读取到的图片由BGR转换成RGB，并传入模型
    results = face_detector.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 遍历检测到的人脸并绘制矩形框
    if results.detections:
        if len(results.detections) > 1:
            for face in results.detections:
                box = face.location_data.relative_bounding_box
                xmin, ymin, width, height = [box.xmin, box.ymin, box.width, box.height]
                cv2.rectangle(img, (int(xmin * width_), int(ymin * height_)),
                              (int((xmin + width) * width_), int((ymin + height) * height_)),
                              (255, 255, 255), 1)
                const_face_list.append([xmin, ymin, width, height])
            face_list = list(results.detections)
            face_list.sort(key=lambda x: x.location_data.relative_bounding_box.width,
                           reverse=True)
            face_main = face_list[0]
        else:
            face_main = results.detections[0]
        box = face_main.location_data.relative_bounding_box
        xmin, ymin, width, height = [box.xmin, box.ymin, box.width, box.height]
        if xmin + width / 2 <= 0.3:
            direction = 1
        elif xmin + width / 2 >= 0.7:
            direction = 2
        elif ymin + height / 2 <= 0.3:
            direction = 3
        elif ymin + height / 2 >= 0.7:
            direction = 4
        const_face_list.append([xmin, ymin, width, height])
        # 这里如果用mp_drawing.draw_detection(img, face)可绘制面部关键点
        cv2.rectangle(img, (int(xmin * width_), int(ymin * height_)),
                      (int((xmin + width) * width_), int((ymin + height) * height_)),
                      (0, 255, 0), 2)
    else:
        direction = -1


def draw_const_face(img):
    if const_face_list:
        for face in const_face_list[:-1:]:
            xmin, ymin, width, height = face
            cv2.rectangle(img, (int(xmin * width_), int(ymin * height_)),
                          (int((xmin + width) * width_), int((ymin + height) * height_)),
                          (255, 255, 255), 1)
        xmin, ymin, width, height = const_face_list[-1]
        cv2.rectangle(img, (int(xmin * width_), int(ymin * height_)),
                      (int((xmin + width) * width_), int((ymin + height) * height_)),
                      (0, 255, 0), 2)


def voice_announce(message):
    engine = pyttsx3.init()
    engine.say(message)
    engine.runAndWait()


def realize_announce():
    global direction
    global judge_announce
    while not judge_shoot.value:
        if direction == 1:
            voice_announce("向右")
            direction = 0
        elif direction == 2:
            voice_announce("向左")
            direction = 0
        elif direction == 3:
            voice_announce("向下")
            direction = 0
        elif direction == 4:
            voice_announce("向上")
            direction = 0
        elif direction == -1:
            voice_announce("看不到你")
            direction = 0
    judge_announce = True


def realize_speech(goal, r_, judge_shoot_):
    model_size = "../../face_detect/faster-whisper-webui/models/faster-whisper/faster-whisper-tiny"
    model_ = WhisperModel(model_size, device="cpu", compute_type="int8")
    voice_announce("欢迎开启智慧拍照")
    while not judge_shoot_.value:
        with sr.Microphone() as mic_:
            data = r_.listen(mic_, phrase_time_limit=8)
        try:
            with open("output.wav", "wb") as f:
                f.write(data.get_wav_data())
            start = time.time()
            # initial_prompt="拍照"
            segments, info = model_.transcribe("output.wav", language="zh", initial_prompt="拍")
            print(f"trans_duration: {time.time() - start}s")
            for segment in segments:
                print(f"trans_text: {segment.text}")
                if goal in segment.text:
                    judge_shoot_.value = True
                    return None
        except Exception:
            continue


def realize_face():
    global detect_sign
    global width_, height_

    # phone_camera = "http://admin:admin@192.168.43.1:8081/"
    cap = cv2.VideoCapture(0)
    width_ = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height_ = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    while True:
        ret, image = cap.read()
        if not ret:
            break
        image = cv2.flip(image, 1)
        dst_image = image.copy()
        if detect_sign % 10 == 0:
            const_face_list.clear()
            detect_face(image)
            detect_sign = 1
        else:
            draw_const_face(image)
        cv2.imwrite("image_data/picture.jpg", image)
        detect_sign += 1
        # cv2.imshow(window_name, image)
        if cv2.waitKey(3) == 32:
            judge_shoot.value = True
        if judge_shoot.value:
            # cv2.imshow(window_name, dst_image)
            while True:
                if judge_announce:
                    cv2.imwrite("image_data/picture.jpg", dst_image)
                    voice_announce("拍照成功")
                    break
            cv2.waitKey(3000)
            cv2.imwrite("image_data/image_0.jpg", dst_image)
            break
    cv2.destroyAllWindows()


def final_realize_shoot():
    realize_face_thread = threading.Thread(target=realize_face)

    realize_face_thread.start()

    realize_speech_process = multiprocessing.Process(target=realize_speech,
                                                     args=("拍照", r, judge_shoot),
                                                     daemon=True)

    realize_announce_thread = threading.Thread(target=realize_announce, daemon=True)

    realize_speech_process.start()
    realize_announce_thread.start()

    realize_face_thread.join()
    voice_announce_thread()
    image_understanding("image_data/image_", "jpg", 1, 0,
                        "请你内容、光线、色彩、构图等方面评价我这幅照片。", True)


if __name__ == "__main__":
    speech_recognize_init()
    final_realize_shoot()
