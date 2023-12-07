import threading
import time
import speech_recognition as sr
import cv2
from faster_whisper import WhisperModel
from p3_ImageUnderstanding import image_understanding, spark_chat
from p3_match_and_stitcher import judge_equal_realize
from p3_shoot import voice_announce, speech_recognize_init
from place_365.app import predict_realize, calc_most_proba_scene


input_info_grace = "我拍了一张图片，请用优美的自然语言对它进行描述，字数在三十到五十字之间。请你仅仅描述图片，不要输出别的话。这张图片的特征有："
input_info_object = "请以第二人称，用客观的自然语言描述一下我当前所处的环境，字数在五十字到一百字之间。请你仅仅描述我所处的环境，不要输出别的话。我所处的环境的特征有："
track_catch = 0
track_under = 0
video_close = False
start = 0
finish = 0

model_size = "../../face_detect/faster-whisper-webui/models/faster-whisper/faster-whisper-tiny"
model = WhisperModel(model_size, device="cpu", compute_type="int8")
r = sr.Recognizer()
scene_list = []


def speech_listen(filepath):
    print("录音开始")
    with sr.Microphone() as mic:
        data = r.listen(mic, timeout=4, phrase_time_limit=8)
    print("录音结束")
    with open(filepath, "wb") as f:
        f.write(data.get_wav_data())


def faster_whisper_recognize(out_audio, r_, initial_prompt_):
    global r
    r = r_
    try:
        speech_listen("output.wav")
        print("transcribe_start")
        start_ = time.time()
        segments, info = model.transcribe(out_audio, beam_size=5, language="zh",
                                          initial_prompt=initial_prompt_)
        print(f"trans_duration: {time.time() - start_}s")
    except sr.WaitTimeoutError as e:
        print(e)
        segments = []
    return segments


def image_catch(key_value_):
    global track_catch, video_close
    global start, finish
    # "http://admin:admin@192.168.43.1:8081"
    cap = cv2.VideoCapture(0)
    num = 0

    voice_announce("录像开始")
    ret, trainImage = cap.read()
    if not ret:
        return None
    flip_image = cv2.flip(trainImage, 1)
    cv2.imwrite("image_data/picture.jpg", flip_image)
    cv2.imwrite(f"image_data/image_{num}.jpg", trainImage)
    track_catch += 1
    num += 1
    scene_list.append(predict_realize(trainImage))
    start = time.time()
    temp = time.time()
    key_value_.value = False
    while num < 8 and (not key_value_.value):
        ret, image = cap.read()
        if not ret:
            break
        if time.time() - temp >= 2.5:
            if judge_equal_realize(image, trainImage):
                break
        flip_image = cv2.flip(image, 1)
        cv2.imwrite("image_data/picture.jpg", flip_image)
        if time.time() - temp >= 3:
            temp = time.time()
            cv2.imwrite(f"image_data/image_{num}.jpg", image)
            track_catch += 1
            num += 1
            scene_list.append(predict_realize(image))
        cv2.waitKey(3)
    finish = time.time()
    voice_announce("录像结束，开始识别周围环境")
    video_close = True
    cv2.destroyAllWindows()


def image_catch_thread(key_value_):
    img_catch_thread = threading.Thread(target=image_catch, args=(key_value_, ))
    img_catch_thread.start()


# 以下是用faster_whisper识别语音
def faster_whisper_speech(goal):
    voice_announce("请说环境识别。我将开始识别当前环境")
    while True:
        try:
            segments = faster_whisper_recognize("output.wav", r, "环境识别")
            for segment in segments:
                print(f"text: {segment.text}")
                if goal in segment.text:
                    voice_announce("好的。听到录像开始后请缓慢地转动镜头，总时长二十四秒。我将根据镜头的画面识别当前环境。当画面重复时我会自动停止")
                    return True
        except Exception:
            continue


# 最终实现
def final_realize_IA(answer_value_, key_value_):
    global track_under, track_catch, video_close
    answer_value_.value = "以下是视界之声对照片或您所处环境的描述：\n    "
    track_under = 0
    track_catch = 0
    video_close = False
    voice_announce("好的。听到录像开始后请缓慢地转动镜头，总时长二十四秒。我将根据镜头的画面识别当前环境。当画面重复时我会自动停止")
    img_data_list = []
    image_catch_thread(key_value_)
    while True:
        if track_under < track_catch:
            img_data_list.extend(image_understanding("image_data/image_", "jpg", 1, track_under))
            track_under += 1
        elif video_close:
            break
    curr_scene = calc_most_proba_scene(scene_list)
    spark_chat(img_data_list, curr_scene, answer_value_)
    print(f"Time image capture takes: {finish - start}s")


if __name__ == '__main__':
    # r = speech_recognize_init()
    # final_realize_IA()
    pass
