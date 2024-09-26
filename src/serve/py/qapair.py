from excelProcess import get_sheet_names, read_sheet_by_attrs
import llmQA as llm
from XFllm import generate_answer
import sentence2Vec as s2v
import json
import multthreads as mthreads
from time import time
import numpy as np
import ast
import mongServe as mg

excel_path = r".\问制度 问题和回答填写表.xlsx"  # 问答对路径
json_path = r"QA_pairs.json"  # 存储json的路径

threads_num = 4
# 读取json文件
with open("./config.json", "r") as f:
    data = json.load(f)
    threads_num = data["seq_threads_num"]


def addpairQA(file_path):
    # 存储问答对
    # excel每一列的名字
    attrs = ["文件名", "问题", "回答"]
    qa_pairs = mg.fetch_alldata_db("qapair")
    for sheet_name in get_sheet_names(file_path):
        data = read_sheet_by_attrs(file_path, sheet_name, attrs)
        qa_pairs.extend(data)

    params = []
    for qa_pair in qa_pairs:
        text = f"文件名:{qa_pair['文件名']}\n问题:{qa_pair['问题']}"
        # qa_pair["embedding"] = embedding_generate(text, model)
        params.append(text)

    results = mthreads.multThreads(s2v.embedding_generate, params, threads_num)
    for i in range(len(qa_pairs)):
        qa_pairs[i]["embedding"] = str([x for x in results[i]])

    # 存储到数据库中
    # with open(r"QA_pairs.json", "w", encoding="utf-8") as f:
    # json.dump(qa_pairs, f, ensure_ascii=False, indent=4)
    mg.insert_data_clear("qapair", qa_pairs)


def pairQA(user_input):
    # 从mongo中读取数据
    # （现在是json数据）
    # with open(json_path, "r", encoding="utf-8") as f:
    #     qa_pairs = json.load(f)
    qa_pairs = mg.fetch_alldata_db("qapair")

    start_time = time()
    query_embedding = s2v.embedding_generate(user_input)

    vector_data = [ast.literal_eval(doc["embedding"]) for doc in qa_pairs]

    # # 将向量数据转换为 numpy 数组
    vector_array = np.array(vector_data)

    # qa_pairs["embedding"] = [np.array(eval(doc["embedding"])) for doc in qa_pairs]
    # 查找前5个语义相似度最近的问答对
    results = []
    # for qa_pair in qa_pairs:
    for i in range(len(qa_pairs)):
        embedding = np.array(vector_array[i])
        qa_pairs[i]["embedding"] = embedding
        similarity = query_embedding @ embedding.T
        results.append((similarity, qa_pairs[i]))

    # 按照相似度从大到小排序
    results.sort(key=lambda x: x[0], reverse=True)
    end_time = time()
    for i in range(5):
        print(
            f"问题{i+1}：{results[i][1]['问题']}, 来源：{results[i][1]['文件名']}, 相似度：{results[i][0]:.4f}"
        )

    for i in range(5):
        # 大模型判定
        question = f"这是用户提出的问题：{user_input}\n请判断以下的候选问题中是否存在与用户的问题一致的问题，如果一致，请输出问题的序号，否则输出-1：\n\
            问题1：{results[0][1]['问题']}， 文件: {results[0][1]['文件名']}\n\
            问题2：{results[1][1]['问题']}， 文件: {results[1][1]['文件名']}\n\
            问题3：{results[2][1]['问题']}， 文件: {results[2][1]['文件名']}\n\
            问题4：{results[3][1]['问题']}， 文件: {results[3][1]['文件名']}\n\
            问题5：{results[4][1]['问题']}， 文件: {results[4][1]['文件名']}\n\n"

        answer_format = f"只需要输出最一致的问题，输出格式: <Answer>1</Answer>\n"
        example = "例如：3是和用户问题最一致的，输出<Answer>3</Answer>"

        try:
            # answer = llm.chatmodel(question + answer_format + example)
            answer = generate_answer(question + answer_format + example)
        except:
            # answer = llm.zhipuChat(question + answer_format + example)
            answer = "<Answer>-1</Answer>"

        try:
            ans = int(answer.split("<Answer>")[1].split("</Answer>")[0])
            print(ans)
            print(f"查询时间：{end_time - start_time:.4f}秒")
            break
        except:
            ans = -1
    return "None" if ans == -1 else results[ans - 1][1]["回答"]


if __name__ == "__main__":
    # print(pairQA("罚没卷烟的收购价格是如何计算的？"))
    addpairQA(excel_path)
