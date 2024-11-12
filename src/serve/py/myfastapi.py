from fastapi import FastAPI, WebSocket
import uvicorn
import asyncio
from openai import OpenAI


app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()

        api_key = "32a9f0f0372792bc0aa4a50fdc023462.lyB6j4K3pESjEIgM"
        api_base = "https://open.bigmodel.cn/api/paas/v4/"
        client = OpenAI(api_key=api_key, base_url=api_base)
        response = client.chat.completions.create(
            model="glm-4-flash",  # 可以替换为你想使用的模型
            messages=[{"role": "user", "content": data}],
            stream=True,  # 开启流式响应
        )

        answers = ""
        for chunk in response:
            # print(1)
            chunk_message = chunk.choices[0].delta.content
            answers += chunk_message
            json_data = json.dumps({"isOK": False, "message": chunk_message})
            await websocket.send_text(f"{json_data}")
            await asyncio.sleep(0.1)  # 模拟延迟
            print(chunk_message, end="", flush=True)
        await websocket.send_text("DONE")


import time
import json
from index import (
    reQuery,
    preAnswer,
    keyWord,
    RRF,
    wordVec,
    euDistance,
    reOrder,
    ansSplit,
    quotesMap,
)
import llmQA as llmqa


@app.websocket("/QA")
async def QandA(websocket: WebSocket):
    await websocket.accept()
    while True:
        input_data = await websocket.receive_json()
        # input_data = json.dumps(input_data)
        print(input_data)

        questions = input_data["questions"]
        original_query = questions

        # 检索参考值 0为关键词;1为余弦相似度;2为欧氏距离
        searchWay = input_data["searchWay"]
        # 检索强度
        searchWeight = input_data["searchWeight"]
        outKnowledge = ""
        most_similar_data = ""
        # 是否优化提问
        reAsk = input_data["reAsk"]
        # 是否预回答优化
        preAns = input_data["preAns"]
        # 是否使用混合检索
        isRRF = input_data["isRRF"]
        # 是否重排
        isReOrder = input_data["isReOrder"]

        time_start = time.time()  # 开始计时

        # answers = qap.pairQA(questions)
        answers = "None"
        quoteList = []
        if answers != "None":
            questions += answers
        elif reAsk == True:
            print("重提问")
            questions = reQuery(questions)
        elif preAns == True:
            print("预回答")
            questions = preAnswer(questions)

        print(questions)

        # 选择检索方法
        if isRRF:
            print("混合检索")
            # 混合检索
            most_similar_data = RRF(
                keyWord(questions, searchWeight),
                wordVec(questions, searchWeight),
                euDistance(questions, searchWeight),
                searchWeight,
            )

        elif searchWay == 0:
            print("关键词检索")
            most_similar_data = keyWord(questions, searchWeight)
        elif searchWay == 1:
            print("余弦相似度检索")
            most_similar_data = wordVec(questions, searchWeight)
        elif searchWay == 2:
            print("欧氏距离检索")
            most_similar_data = euDistance(questions, searchWeight)

        # 重排
        if isReOrder:
            print("重排")
            quotes = most_similar_data[: 10 * searchWeight]
            print("重排数组长度:", len(quotes))
            most_similar_data = reOrder(questions, quotes)

        # 资料引用
        quoteList = most_similar_data[: 2 * searchWeight]
        outKnowledge = ""

        time_end = time.time()  # 结束计时
        time_c = time_end - time_start  # 运行所花时间
        print("检索 cost", time_c, "s")

        # 问答准备
        if answers == "None":
            # time_start = time.time()  # 开始计时
            nowlen = 0
            for q in quoteList:
                if nowlen + len(q["sentence"]) < 4096:
                    outKnowledge += q["sentence"]
                    nowlen = nowlen + len(q["sentence"])
                else:
                    break
            # print("检索资料：", outKnowledge)
            prompts = (
                "你是一名文件数据管理人员，需要对用户的问题根据资料精准得回答，如果资料中得不出结论，就不要回答，下面是相关的资料：\n"
                + outKnowledge
            )

            user_input = prompts + "下面是用户的问题，请回答：" + original_query

            print("问题长度：", len(user_input))
            # response_message = llmqa.zhipuChat(user_input)

            # 如果不能连上本地大模型就用zhipu模型
            # try:
            #     response_message = llmqa.zhipuChat(user_input)
            #     # response_message = llmqa.chatmodel(user_input)
            #     # response_message = generate_answer(user_input)
            # except:
            #     print("大模型出错")
            #     # response_message = llmqa.zhipuChat(user_input)
            #     response_message = "err"
            # answers = str(response_message)

            api_key = "32a9f0f0372792bc0aa4a50fdc023462.lyB6j4K3pESjEIgM"
            api_base = "https://open.bigmodel.cn/api/paas/v4/"
            client = OpenAI(api_key=api_key, base_url=api_base)
            response = client.chat.completions.create(
                model="glm-4-flash",  # 可以替换为你想使用的模型
                messages=[{"role": "user", "content": user_input}],
                stream=True,  # 开启流式响应
            )

            answers = ""
            for chunk in response:
                # print(1)
                chunk_message = chunk.choices[0].delta.content
                answers += chunk_message
                # await websocket.send_text(f"{chunk_message}")
                json_data = json.dumps({"isOK": False, "message": chunk_message})
                await websocket.send_text(f"{json_data}")
                await asyncio.sleep(0.1)  # 模拟延迟
                print(chunk_message, end="", flush=True)
                # json_data = json.dumps({"message": chunk_message})

            # time_end = time.time()  # 结束计时
            # time_c = time_end - time_start  # 运行所花时间
            # print("回答 cost", time_c, "s")

        # 对回答进行处理
        ansArr = ansSplit(answers)
        # print("ansArr：", ansArr)
        time_start = time.time()  # 开始计时

        (newQuoteList, textWithQuote) = quotesMap(ansArr, quoteList)

        time_end = time.time()  # 结束计时
        time_c = time_end - time_start  # 运行所花时间
        print("处理回答 cost", time_c, "s")
        json_data = json.dumps(
            {
                "isOK": True,
                "answers": answers,
                "quote": list(newQuoteList),
                "textWithQuote": list(textWithQuote),
            }
        )
        await websocket.send_text(json_data)
        # -----------------------------------------------------------
        # else:
        #     newQuoteList = []
        #     textWithQuote = [{"text": answers, "quote": -1}]

        # return jsonify(
        #     {
        #         "answers": answers,
        #         "quote": list(newQuoteList),
        #         "textWithQuote": list(textWithQuote),
        #     }
        # )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7777)
