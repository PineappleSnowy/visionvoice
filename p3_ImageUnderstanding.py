import threading
import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
import websocket  # 使用websocket_client
import os
from p3_num_to_zh import num_to_zh
import pyttsx3


appid = "3c1ed4b2"  # 填写控制台中获取的 APPID 信息
api_secret = "MWJlZmU0NTdhNGIwMjYyYmM5YjI4NWYz"  # 填写控制台中获取的 APISecret 信息
api_key = "24b916c096bda93d9da64ae6909cd35f"  # 填写控制台中获取的 APIKey 信息

imageunderstanding_url = "wss://spark-api.cn-huabei-1.xf-yun.com/v2.1/image"  # 图片理解云端环境的服务地址
spark_url = "ws://spark-api.xf-yun.com/v3.1/chat"  # 星火大模型3.1云端环境的服务地址
text = []
answer = ""
domain = ""
temp_answer_list = []
answer_lock = threading.Lock()
judge_ws_close = False


class WsParam(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, url_):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(url_).netloc
        self.path = urlparse(url_).path
        self.img_or_chat_url = url_

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.img_or_chat_url + '?' + urlencode(v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        return url


# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws, one, two):
    global judge_ws_close
    judge_ws_close = True
    print(" ")


# 收到websocket连接建立的处理
def on_open(ws):
    run_thread = threading.Thread(target=run, args=(ws, ))
    run_thread.start()


def run(ws, *args):
    data = json.dumps(gen_params(appid_=ws.appid, question=ws.question))
    ws.send(data)


# 收到websocket消息的处理
def on_message(ws, message):
    # print(message)
    data = json.loads(message)
    code = data['header']['code']
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    else:
        choices = data["payload"]["choices"]
        status = choices["status"]
        content = choices["text"][0]["content"]
        print(content, end="")
        global answer
        temp_answer_list.append(content)
        answer += content
        if status == 2:
            ws.close()


def gen_params(appid_, question):
    """
    通过appid和用户的提问来生成请参数
    """
    data = {
        "header": {
            "app_id": appid_,
            # "uid": "12345"
        },
        "parameter": {
            "chat": {
                "domain": domain,
                "temperature": 0.5,
                "top_k": 4,
                "max_tokens": 2048,
                "auditing": "default"
            }
        },
        "payload": {
            "message": {
                "text": question
            }
        }
    }
    return data


def main_image(appid_, api_key_, api_secret_, Imageunderstanding_url, imagedata, question):
    wsParam = WsParam(appid_, api_key_, api_secret_, Imageunderstanding_url)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.appid = appid
    ws.imagedata = imagedata
    ws.question = question
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


def main_chat(appid_, api_key_, api_secret_, Spark_url, question):
    wsParam = WsParam(appid_, api_key_, api_secret_, Spark_url)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.appid = appid
    ws.question = question
    ws.domain = domain
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


def getText(role, content):
    jsoncon = {"role": role, "content": content}
    text.append(jsoncon)
    return text


def getlength(text_):
    length = 0
    for content in text_:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length


def checklen(text_):
    while getlength(text_[1:]) > 8000:
        del text_[1]
    return text_


def image_understanding(img_name_prefix: str, img_type: str, max_img_amount: int, start_index: int) -> list[str]:
    """
    notice: 传入的图片文件必须是前缀+数字+类型的命名形式，且需以start_index开始连续命名，如"picture_0.jpg"、"images/picture_1.jpg"

    initial_prompt: "请用客观真实的语言描述一下这幅图片包含的信息"

    :param img_name_prefix: 传入的图片文件的前缀，前缀可包含文件路径，如图片"images/img_1.jpg"的前缀为"images/img_"
    :param img_type: 图片类型，如"jpg"
    :param max_img_amount: 可接受的最大图片数量，可大于实际图片数
    :param start_index: 图片文件名起始下标
    :return: 对逐张图片的描述组成的列表
    """
    global answer, domain
    domain = "image"
    answer_list = []
    for i in range(start_index, start_index + max_img_amount):
        if os.path.exists(f"{img_name_prefix}{i}.{img_type}"):
            imagedata = open(f"{img_name_prefix}{i}.{img_type}", 'rb').read()
            text.append({"role": "user", "content": str(base64.b64encode(imagedata), 'utf-8'), "content_type": "image"})
            Input = "请你用客观、真实、简洁的语言概括这幅图片所包含的信息。"
            question = checklen(getText("user", Input))
            main_image(appid, api_key, api_secret, imageunderstanding_url, imagedata, question)
            answer_list.append(answer)
            answer = ""
            text.clear()
        else:
            break
    return answer_list


def spark_chat(img_data_list: list[str]) -> str:
    """
    initial_prompt: "我在我身处的环境中拍了几张图片，请你根据这些图片的信息用客观真实的语言描述一下我当前所处的环境。以下是这些图片的信息。"

    :param img_data_list: 包含对逐张图片的描述的字符串列表
    :return: 对环境信息的综述
    """
    global domain
    domain = "generalv3"
    temp_answer_list.clear()
    Input = "我在我身处的环境中拍了几张图片，这几张图片可能有重复和矛盾的部分，请筛查并提取真实简练的图片信息。\
    请你根据提取后的图片信息用客观真实的语言描述一下我当前所处的环境，100字左右。\
    请你仅仅描述我当前所处的环境，不要输出别的话。以下是这些图片的信息。"
    for i, num in zip(img_data_list, range(len(img_data_list))):
        zh_num = num_to_zh(num + 1)
        Input += ("第" + zh_num + "张：" + i)
    question = checklen(getText("user", Input))
    voice_announce_thread()
    main_chat(appid, api_key, api_secret, spark_url, question)
    return answer


def voice_announce_block():
    engine = pyttsx3.init()
    index = 0
    while True:
        if len(temp_answer_list) > index:
            message = temp_answer_list[index]
            engine.say(message)
            engine.runAndWait()
            index += 1
        elif judge_ws_close and (len(temp_answer_list) != 0):
            break


def voice_announce_thread():
    voice_thread = threading.Thread(target=voice_announce_block, args=())
    voice_thread.start()


if __name__ == '__main__':
    data_list = image_understanding("img_", "jpg", 3, 0)
    description = spark_chat(data_list)
