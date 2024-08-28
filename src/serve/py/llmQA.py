from zhipuai import ZhipuAI
import requests
import json

llm_url = "http://192.168.3.118:5000/ChatQA"
# 读取json文件
with open("./config.json", "r") as f:
    data = json.load(f)
    llm_url = data["llm_url"]


# 智谱模型
def zhipuChat(input):
    print("智谱called")
    client = ZhipuAI(
        api_key="ca48767be5d0dbc41b3a135f7be786da.w5O4CRLo111zUlbj"
    )  # 填写您自己的APIKey

    messages = []
    messages += [{"role": "user", "content": input}]
    response = client.chat.completions.create(
        model="glm-4", messages=messages  # 填写需要调用的模型名称
    )
    return response.choices[0].message.content


def chatmodel(query):
    print("llm called")
    url = llm_url
    datas = {"questions": query}
    datas = json.dumps(datas)
    head = {"Content-Type": "application/json"}
    return requests.post(url, data=datas, headers=head).json()["answers"]
