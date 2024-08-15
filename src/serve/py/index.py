from flask import Flask, request, jsonify, make_response, send_file, Response
from flask_cors import CORS
import os
import io
import re
import subprocess
import time
import fitz  # PyMuPDF
import win32com.client as win32
import jieba  # 分词

app = Flask(__name__)
CORS(app)
import pythoncom
import getSeq
import myTools
import sentence2Vec
import mongServe as mg
from zhipuai import ZhipuAI
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import ast
from bson import ObjectId, json_util
import reranker as rerank
import requests
import json

file_path = "D:\data\\"

# 读取json文件
with open("./config.json", "r") as f:
    data = json.load(f)
    file_path = data["file_path"]


def convert_word_to_pdf(input_path, output_path):
    pythoncom.CoInitialize()
    # 创建Word应用程序实例
    pdf_file = os.path.join(
        output_path, os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
    )
    word_app = win32.gencache.EnsureDispatch("Word.Application")
    # 设置应用程序可见性为False（不显示Word界面）
    word_app.Visible = False
    try:
        # 打开Word文档
        doc = word_app.Documents.Open(input_path)
        print(pdf_file)
        # 保存为PDF
        doc.SaveAs(pdf_file, FileFormat=17)
        doc.Close()
        return True
    except Exception as e:
        print("转换失败：" + str(e))
        return False
    finally:
        # 关闭Word应用程序
        word_app.Quit()


def convert_ofd_to_pdf(ofd_file, output_dir):
    pdf_file = os.path.join(
        output_dir, os.path.splitext(os.path.basename(ofd_file))[0] + ".pdf"
    )
    doc = fitz.open(ofd_file)
    pdf_bytes = doc.convert_to_pdf()
    with open(pdf_file, "wb") as f:
        f.write(pdf_bytes)
    return pdf_file


def chatmodel(query):
    url = "http://192.168.3.118:5000/ChatQA"
    datas = {"questions": query}
    datas = json.dumps(datas)
    head = {"Content-Type": "application/json"}
    return requests.post(url, data=datas, headers=head).json()["answers"]


# def convert_file_to_pdf(input_file, output_dir):
#     if input_file.endswith('.docx') or input_file.endswith('.doc'):
#         return convert_word_to_pdf(input_file, output_dir)
#     elif input_file.endswith('.ofd'):
#         return convert_ofd_to_pdf(input_file, output_dir)
#     else:
#         raise ValueError("Unsupported file format. Only .docx, .doc and .ofd files are supported.")


# 确保上传目录存在
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def find_text_page_in_pdf(pdf_path, text):
    """
    在 PDF 文件中查找文字并返回所在页码
    """
    document = fitz.open(pdf_path)
    for page_num in range(document.page_count):
        print(page_num)
        page = document.load_page(page_num)
        print(page)
        words = re.split(r"(?<=[  ，。。、.?!\n])", text)
        listW = myTools.remove_newline_items(words)
        print(listW)
        lenWords = len(words)
        lenSearchWord = 0
        for w in words:
            text_instances = page.search_for(w)
            if text_instances:
                lenSearchWord += 1
        if lenSearchWord / lenWords >= 0.5:
            return page_num + 1  # 页码从 1 开始

    # 没找到返回1
    return 1


def find_text_in_pdf(pdf_path, page_num, text):
    """
    在 PDF 文件的指定页面中查找文字并返回矩形块
    """
    document = fitz.open(pdf_path)
    # 检查页面号是否有效
    if page_num <= 1 or page_num > len(document):
        return -1

    page = document.load_page(page_num - 1)
    words = re.split(r"(?<=[  ，。。、.?!\n])", text)
    listW = myTools.remove_newline_items(words)

    res = []
    for w in listW:
        text_instances = page.search_for(w)
        if text_instances:
            # 获取搜索结果的具体信息
            for t in text_instances:
                x0, y0, x1, y1 = t
            temp_text = [x0, y0, x1 - x0, y1 - y0]
            res.append(temp_text)
    return res


@app.route("/filePre", methods=["POST"])
def file_pre():
    file = request.args.get("file")
    text = request.args.get("text")
    outpath = file_path
    pdf_path = f"{outpath}{file}.pdf"
    pdf_blob = myTools.read_pdf_as_blob(pdf_path)
    response = Response(io.BytesIO(pdf_blob), mimetype="application/pdf")
    response.headers.set("Content-Disposition", "attachment", filename="sample.pdf")
    page = find_text_page_in_pdf(pdf_path, text)
    response.headers.set("PageNumber", page)
    print(page)
    pagerects = find_text_in_pdf(pdf_path, page, text)
    response.headers.set("PageRects", pagerects)
    return response


@app.route("/filesave", methods=["POST"])
def file_save():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    print(file)
    # file_path = request.form.get('file_path')
    if file:
        filepath = os.path.join(file_path, file.filename)
        file.save(filepath)
    return "successful"


@app.route("/fileUpload", methods=["POST"])
def file_upload():
    file = request.args.get("file")
    file_name = file.split(".")[1]
    file_name_ori = file.split(".")[0]
    path = file_path + file
    outpath = file_path
    pdf_path = f"{outpath}/{file_name_ori}.pdf"
    docx_path = f"{outpath}/{file_name_ori}.docx"

    # 集合名称
    collection_name = "fileList"
    oriFileData = mg.fetch_data_findone_db(collection_name, "fileName", file_name_ori)
    print(collection_name, "fileName", file_name_ori, oriFileData)
    if (oriFileData == None) | (oriFileData == []):
        mg.insert_data(collection_name, [{"fileName": file_name_ori}])
    if os.path.exists(docx_path):
        docx_blob = myTools.read_pdf_as_blob(docx_path)
        response = Response(
            io.BytesIO(docx_blob),
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        response.headers.set(
            "Content-Disposition", "attachment", filename="sample.docx"
        )
        if not os.path.exists(pdf_path):
            # return send_file(f'{file_path}/{file}', as_attachment=True)
            # 执行文件转换
            convert_word_to_pdf(path, outpath)
        return response
    if os.path.exists(pdf_path):
        print("pdf exists")
        pdf_blob = myTools.read_pdf_as_blob(pdf_path)
        response = Response(io.BytesIO(pdf_blob), mimetype="application/pdf")
        response.headers.set("Content-Disposition", "attachment", filename="sample.pdf")
        return response
    else:
        # return send_file(f'{file_path}/{file}', as_attachment=True)
        # 执行文件转换
        convert_word_to_pdf(path, outpath)

        # # 等待文件创建完成
        for _ in range(30):  # 检查 30 次，每次等待 1 秒，总计 30 秒
            if os.path.exists(pdf_path):
                pdf_blob = myTools.read_pdf_as_blob(pdf_path)
                response = Response(io.BytesIO(pdf_blob), mimetype="application/pdf")
                response.headers.set(
                    "Content-Disposition", "attachment", filename="sample.pdf"
                )
                return response
            time.sleep(1)

        return jsonify({"error": "File conversion timeout"}), 500


@app.route("/wordToSeq", methods=["POST"])
def word2seq():
    file = request.json.get("file").split(".")[0] + ".docx"
    overlap = request.json.get("overlap")
    chunkSize = request.json.get("chunkSize")
    SplitType = request.json.get("SplitType")
    path = file_path + file
    word = myTools.read_word_file(path)
    # single_sentences_list = remove_newline_items(re.split(r'(?<=[。.?!\n\n])\s+', word))

    # sentences = [{'sentence': x, 'index': i} for i, x in enumerate(single_sentences_list)]
    # sentences = getSeq.RCSplit(word, chunkSize, overlap)
    sentence = []
    print(SplitType)
    if SplitType == 0:
        sentences = getSeq.RCSplit(word, chunkSize, overlap)
    else:
        sentences = getSeq.split_documentByOriChunk(word)
    return jsonify(sentences)


@app.route("/chunkWordToSeq", methods=["POST"])
def chunkWordToSeq():
    textData = request.json.get("textData")
    overlap = request.json.get("overlap")
    chunkSize = request.json.get("chunkSize")

    sentence = []
    sentences = getSeq.RCSplit(textData, chunkSize, overlap)
    return jsonify(sentences)


@app.route("/seqToVec", methods=["POST"])
def seq2vec():
    textData = request.json.get("textData")
    fileName = request.json.get("fileName").split(".")[0]
    embeddings = sentence2Vec.embedding_generate([x["sentence"] for x in textData])
    for i, sentence in enumerate(textData):
        sentence["fileName"] = str(fileName)
        sentence["sentence_embedding"] = str([x for x in embeddings[i]])
    # 集合名称
    collection_name = "SeqVector"
    mg.insert_data(collection_name, textData)

    # 集合名称
    collection_name = "fileList"
    oriFileData = mg.updata_data_findone_db(
        collection_name, "fileName", fileName, {"chunkLen": len(textData)}
    )

    return jsonify(["success"])


# def find_most_similar_vectors(vector_array, target_vector, top_n=5):
#     """
#     在向量数组中查找与目标向量最相似的前几个向量

#     :param vector_array: np.ndarray, 向量数组，形状为 (num_vectors, vector_dim)
#     :param target_vector: np.ndarray, 目标向量，形状为 (vector_dim,)
#     :param top_n: int, 要查找的最相似向量的数量
#     :return: list, 最相似向量的索引及其相似度
#     """
#     # 计算目标向量与向量数组中每个向量的余弦相似度
#     similarities = cosine_similarity(
#         vector_array, target_vector.reshape(1, -1)
#     ).flatten()

#     # 获取最相似的前 top_n 个向量的索引
#     most_similar_indices = similarities.argsort()[-top_n:][::-1]

#     # 返回最相似向量的索引及其相似度
#     most_similar_vectors = [
#         (index, similarities[index]) for index in most_similar_indices
#     ]
#     return most_similar_vectors


# def find_similar_vectors(vector_array, target_vector, top_n, holdValue):
#     """
#     在向量数组中查找与目标向量最相似的前几个向量
#     找到前n个其中前n个向量的相似度相加大于等于holdValue

#     :param vector_array: np.ndarray, 向量数组，形状为 (num_vectors, vector_dim)
#     :param target_vector: np.ndarray, 目标向量，形状为 (vector_dim,)
#     :param top_n: int, 要查找的最相似向量的数量
#     :return: list, 最相似向量的索引及其相似度
#     """
#     # 计算目标向量与向量数组中每个向量的余弦相似度
#     similarities = cosine_similarity(
#         vector_array, target_vector.reshape(1, -1)
#     ).flatten()

#     # 排序
#     sorted_indices = similarities.argsort()

#     # 阈值
#     nowValue = 0.0
#     nValue = 0

#     while nowValue <= holdValue and nValue < top_n:
#         nValue += 1
#         nowValue += similarities[sorted_indices[-nValue]]

#     # 获取最相似的前 top_n 个向量的索引
#     most_similar_indices = sorted_indices[-nValue:][::-1]

#     # 返回最相似向量的索引及其相似度
#     most_similar_vectors = [
#         (index, similarities[index]) for index in most_similar_indices
#     ]
#     print("most_similar_vectors:", most_similar_vectors)
#     return most_similar_vectors


def remove_special_characters(strings):
    """
    处理掉列表中的特殊字符
    """
    special_characters = "!@#$%^&*()_+{}[]|\:;'<>?,./\"，；。？！”“的了呢么吗"
    return [
        string
        for string in strings
        if not any(char in special_characters for char in string)
    ]


# 混合检索
def RRF(order1, order2, order3):

    # 获取数据
    collection_name = "SeqVector"
    allData = mg.fetch_vectors_from_db(collection_name)

    Len = len(order1)
    score = [0.0] * Len

    # RRF算法直接重排
    for i in range(0, Len):
        score[order1[i]["order"]] += 1.0 / (i + 1)
        score[order2[i]["order"]] += 1.0 / (i + 1)
        score[order3[i]["order"]] += 1.0 / (i + 1)

    sorted_rrf = np.array(score).argsort()[::-1]

    most_similar_data = []
    for index in sorted_rrf:
        vector_doc = allData[index]
        vector_doc["_id"] = str(vector_doc["_id"])
        vector_doc["order"] = int(index)
        # vector_doc = mg.fetch_data_findone_db(collection_name,'index',int(index))
        most_similar_data.append(vector_doc)

    return most_similar_data


# 重排
def reOrder(questions):
    # 获取数据
    collection_name = "SeqVector"
    allData = mg.fetch_vectors_from_db(collection_name)

    q = []
    for i in allData:
        q.append([questions, i["sentence"]])
    sorted_reScore = np.array(rerank.rerankerStore(q)).argsort()[::-1]

    most_similar_data = []
    for index in sorted_reScore:
        vector_doc = allData[index]
        vector_doc["_id"] = str(vector_doc["_id"])
        vector_doc["order"] = int(index)
        # vector_doc = mg.fetch_data_findone_db(collection_name,'index',int(index))
        most_similar_data.append(vector_doc)

    return most_similar_data


"""

检索方法函数
"""


# 关键词检索
def keyWord(questions):
    # 先把questions分割成几个关键词
    questionsList = remove_special_characters(jieba.lcut_for_search(questions))
    print("分词结果", questionsList)
    # 处理掉空格和标点符号

    # 获取数据
    collection_name = "SeqVector"
    allData = mg.fetch_vectors_from_db(collection_name)

    weight = [0] * len(allData)
    # 然后在各个部分查找这些词语
    for q in questionsList:
        for i in range(len(allData)):
            if q in allData[i]["sentence"]:
                weight[i] += 1

    # 排序
    sorted_word = np.array(weight).argsort()[::-1]

    most_similar_data = []
    for index in sorted_word:
        vector_doc = allData[index]
        vector_doc["_id"] = str(vector_doc["_id"])
        vector_doc["order"] = int(index)
        # vector_doc = mg.fetch_data_findone_db(collection_name,'index',int(index))
        most_similar_data.append(vector_doc)

    return most_similar_data


# 余弦相似度检索
def wordVec(questions):
    queVec = sentence2Vec.embedding_generate(questions)

    collection_name = "SeqVector"
    allData = mg.fetch_vectors_from_db(collection_name)
    vector_data = [ast.literal_eval(doc["sentence_embedding"]) for doc in allData]
    # # 将向量数据转换为 numpy 数组
    vector_array = np.array(vector_data)
    target_vector = np.array(queVec)

    # 计算目标向量与向量数组中每个向量的余弦相似度
    similarities = cosine_similarity(
        vector_array, target_vector.reshape(1, -1)
    ).flatten()

    # 排序
    sorted_indices = similarities.argsort()[::-1]
    # most_similar = [(index, similarities[index]) for index in sorted_indices]

    most_similar_data = []
    for index in sorted_indices:
        vector_doc = allData[index]
        vector_doc["_id"] = str(vector_doc["_id"])
        vector_doc["order"] = int(index)
        # vector_doc = mg.fetch_data_findone_db(collection_name,'index',int(index))
        most_similar_data.append(vector_doc)

    return most_similar_data


# 欧氏距离
def euDistance(questions):
    queVec = sentence2Vec.embedding_generate(questions)

    collection_name = "SeqVector"
    allData = mg.fetch_vectors_from_db(collection_name)
    vector_data = [ast.literal_eval(doc["sentence_embedding"]) for doc in allData]
    # # 将向量数据转换为 numpy 数组
    vector_array = np.array(vector_data)
    target_vector = np.array(queVec)

    euclidean_distance = []
    for vec in vector_array:
        # 使用 NumPy 的 linalg 模块计算欧氏距离
        euclidean_distance.append(np.linalg.norm(vec - target_vector.reshape(1, -1)))

    # print(euclidean_distance)

    # 排序
    sorted_euclidean_distance = np.array(euclidean_distance).argsort()

    most_similar_data = []
    for index in sorted_euclidean_distance:
        vector_doc = allData[index]
        vector_doc["_id"] = str(vector_doc["_id"])
        vector_doc["order"] = int(index)
        # vector_doc = mg.fetch_data_findone_db(collection_name,'index',int(index))
        most_similar_data.append(vector_doc)

    return most_similar_data


# 优化回答
def reQuery(questions):
    # client = ZhipuAI(
    #     api_key="ca48767be5d0dbc41b3a135f7be786da.w5O4CRLo111zUlbj"
    # )  # 填写您自己的APIKey
    # 优化提问
    messages = []
    user_input = (
        "你是一名文件数据管理人员，需要对用户的问题重新表达\n下面是用户的问题，请对其进行重新表述："
        + questions
    )
    # messages += [{"role": "user", "content": user_input}]

    # response = client.chat.completions.create(
    #     model="glm-4", messages=messages  # 填写需要调用的模型名称
    # )
    # response_message = response.choices[0].message.content
    # print(response_message)
    response_message = chatmodel(user_input)

    return questions + "\n" + response_message


# 预回答
def preAnswer(questions):
    # client = ZhipuAI(
    #     api_key="ca48767be5d0dbc41b3a135f7be786da.w5O4CRLo111zUlbj"
    # )  # 填写您自己的APIKey
    # 优化提问
    messages = []
    user_input = (
        "你是一名文件数据管理人员，需要对用户的问题精准的回答\n下面是用户的问题，请回答："
        + questions
    )
    # messages += [{"role": "user", "content": user_input}]

    # response = client.chat.completions.create(
    #     model="glm-4", messages=messages  # 填写需要调用的模型名称
    # )
    # response_message = response.choices[0].message.content
    # print(response_message)

    response_message = chatmodel(user_input)

    return questions + "\n" + response_message


@app.route("/getFileList", methods=["GET"])
def getFileList():
    collection_name = "fileList"
    filiList = mg.fetch_alldata_db(collection_name)
    return jsonify(filiList)


@app.route("/getHistory", methods=["GET"])
def getHistory():
    print("getHistory")
    collection_name = "QAHistory"
    filiList = mg.fetch_alldata_db(collection_name)
    return jsonify(filiList)


@app.route("/saveHistory", methods=["POST"])
def saveHistory():
    print("saveHistory")
    mmr = request.json.get("history")
    collection_name = "QAHistory"
    mg.insert_data_clear(collection_name, mmr)
    return jsonify(["success"])
    # collection_name = "QAHistory"
    # filiList = mg.fetch_alldata_db(collection_name)
    # return jsonify(filiList)


@app.route("/getFileTextSeq", methods=["POST"])
def getFileTextSeq():
    fileName = request.json.get("fileName").split(".")[0]
    collection_name = "SeqVector"
    filiList = mg.fetch_data_find_db(collection_name, "fileName", fileName)
    return jsonify(filiList)


@app.route("/FileListDelOne", methods=["POST"])
def FileListDelOne():
    print(111)
    fileName = request.json.get("fileName").split(".")[0]
    collection_name = "fileList"
    mg.del_data_db(collection_name, "fileName", fileName)
    filiList = mg.fetch_alldata_db(collection_name)
    return jsonify(filiList)


@app.route("/QA", methods=["POST"])
def QandA():
    questions = request.json.get("questions")
    original_query = questions

    # 检索参考值 0为关键词;1为余弦相似度;2为欧氏距离
    searchWay = request.json.get("searchWay")
    # 检索强度
    searchWeight = request.json.get("searchWeight")
    outKnowledge = ""
    most_similar_data = ""
    # 是否优化提问
    reAsk = request.json.get("reAsk")
    # 是否预回答优化
    preAns = request.json.get("preAns")
    # 是否使用混合检索
    isRRF = request.json.get("isRRF")
    # 是否重排
    isReOrder = request.json.get("isReOrder")

    if reAsk == True:
        print("重提问")
        questions = reQuery(questions)

    if preAns == True:
        print("预回答")
        questions = preAnswer(questions)

    print(questions)

    outKnowledge = ""
    quoteList = []
    # 选择检索方法

    if isReOrder:
        print("重排")
        most_similar_data = reOrder(questions)
    elif isRRF:
        print("混合检索")
        # 混合检索
        most_similar_data = RRF(
            keyWord(questions), wordVec(questions), euDistance(questions)
        )

    elif searchWay == 0:
        print("关键词检索")
        most_similar_data = keyWord(questions)
    elif searchWay == 1:
        print("余弦相似度检索")
        most_similar_data = wordVec(questions)
    elif searchWay == 2:
        print("欧氏距离检索")
        most_similar_data = euDistance(questions)

    quoteList = most_similar_data[:searchWeight]
    for q in quoteList:
        outKnowledge += q["sentence"]

    messages = []
    # 问答的参数
    # client = ZhipuAI(
    #     api_key="ca48767be5d0dbc41b3a135f7be786da.w5O4CRLo111zUlbj"
    # )  # 填写您自己的APIKey

    prompts = (
        "你是一名文件数据管理人员，需要对用户的问题根据资料精准得回答，如果资料中得不出结论，就不要回答，下面是相关的资料：\n"
        + outKnowledge
    )

    user_input = prompts + "下面是用户的问题，请回答：" + original_query
    # answers = ""

    # messages += [{"role": "user", "content": user_input}]
    # response = client.chat.completions.create(
    #     model="glm-4", messages=messages  # 填写需要调用的模型名称
    # )
    # response_message = response.choices[0].message.content

    response_message = chatmodel(user_input)
    answers = str(response_message)
    # -----------------------------------------------------------
    return jsonify({"answers": answers, "quote": list(quoteList)})


if __name__ == "__main__":
    app.run(debug=True, port=3000)
