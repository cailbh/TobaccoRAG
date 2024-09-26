import asyncio
import websockets

from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
import hmac
from urllib.parse import urlencode
import json


class AssembleHeaderException(Exception):
    def __init__(self, msg):
        self.message = msg


class Url:
    def __init__(this, host, path, schema):
        this.host = host
        this.path = path
        this.schema = schema
        pass


# calculate sha256 and encode to base64
def sha256base64(data):
    sha256 = hashlib.sha256()
    sha256.update(data)
    digest = base64.b64encode(sha256.digest()).decode(encoding="utf-8")
    return digest


def parse_url(requset_url):
    stidx = requset_url.index("://")
    host = requset_url[stidx + 3 :]
    schema = requset_url[: stidx + 3]
    edidx = host.index("/")
    if edidx <= 0:
        raise AssembleHeaderException("invalid request url:" + requset_url)
    path = host[edidx:]
    host = host[:edidx]
    u = Url(host, path, schema)
    return u


# build  auth request url
def assemble_auth_url(requset_url, method="GET", api_key="", api_secret=""):
    u = parse_url(requset_url)
    host = u.host
    path = u.path
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))
    # print(date)
    # print(date)
    # date = "Thu, 12 Dec 2019 01:57:27 GMT"
    signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(
        host, date, method, path
    )
    # print("signature_origin:\n", signature_origin)
    # print(signature_origin)
    signature_sha = hmac.new(
        api_secret.encode("utf-8"),
        signature_origin.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    signature_sha = base64.b64encode(signature_sha).decode(encoding="utf-8")
    authorization_origin = (
        'api_key="%s", algorithm="%s", headers="%s", signature="%s"'
        % (api_key, "hmac-sha256", "host date request-line", signature_sha)
    )
    # print(authorization_origin)
    authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode(
        encoding="utf-8"
    )
    # print(authorization_origin)
    values = {
        "authorization": authorization,
        "host": host,
        "date": date,
    }

    return requset_url + "?" + urlencode(values)


async def spark_chat_answer(
    uri, user_input, role="你是一个智能助手，请根据用户输入回答问题"
):
    # uri = "ws://ai-test.pt.zj.yc/nlp/v1/interact_nlp"  # WebSocket 服务器的 URI
    async with websockets.connect(uri) as websocket:
        # 发送一条消息

        request_body = {
            "header": {
                "app_id": "2e156b98",
                "ctrl": "text_interact",
                "request_id": "xxx",
            },
            "parameter": {
                "nlp": {
                    "type": "xinghuo",
                    "xinghuo": {
                        "systemPromptKey": "xxx",
                        "history": [
                            {"role": "system", "content": f"{role}"},
                            {"role": "user", "content": f"{user_input}"},
                        ],
                    },
                }
            },
            "payload": {"text": {"content": f"{user_input}"}},
        }
        await websocket.send(json.dumps(request_body))

        # 持续接收服务器响应
        answer = ""
        try:
            while True:
                response = await websocket.recv()
                data = json.loads(response)

                text = data["payload"]["nlp"]["answer"]["text"]
                answer += text
                # print(f"{text}", end="", flush=True)
        except websockets.ConnectionClosed as e:
            print(f"Connection closed: {e}")
            print("\n")

        return answer


def generate_answer(user_input, role="你是一个智能助手，请根据用户输入回答问题"):
    # print("xunfei called")
    uri = "ws://ai-test.pt.zj.yc/nlp/v1/interact_nlp"  # WebSocket 服务器的 URI
    api_key = "25403262663f08fd6894211e9448c596"
    api_secret = "OTQ1NzMzNzA3YmM1MDAxYzc4YTliMjJm"
    auth_url = assemble_auth_url(uri, api_key=api_key, api_secret=api_secret)
    return asyncio.run(spark_chat_answer(auth_url, user_input, role))


if __name__ == "__main__":
    # print(generate_answer("你的名字是什么"))
    1
