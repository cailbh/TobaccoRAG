import json
import requests

def generate_answer(url, data):
    headers = {"Content-Type": "application/json"}
    data = json.dumps(data)
    response = requests.post(url, data=data, headers=headers)

    return response.json()["answers"]


if __name__ == "__main__":
    url = "http://192.168.3.118:5000/ChatQA"
    data = {"questions": "杭电是什么"}

    answer = generate_answer(url, data)
    print(answer)
