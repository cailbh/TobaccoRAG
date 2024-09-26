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
import chunk2tree as c2t
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
import qapair as qap
from waitress import serve

file_path = "D:\data\\"
llm_url = "http://192.168.3.118:5000/ChatQA"
threads_num = 16
isWaitress = False
# 读取json文件
with open("./config.json", "r") as f:
    data = json.load(f)
    file_path = data["file_path"]
    llm_url = data["llm_url"]
    threads_num = data["threads_num"]
    isWaitress = data["isWaitress"]


# 模型问答
import llmQA as llmqa
from XFllm import generate_answer


# 文件类型转化
def convert_word_to_pdf(input_path, output_path):
    pythoncom.CoInitialize()
    # 创建Word应用程序实例
    pdf_file = os.path.join(
        output_path, os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
    )
    try:
        # print("wps called")
        word_app = win32.gencache.EnsureDispatch("Kwps.Application")
        print("wps openning")
    except:
        # print("word")
        word_app = win32.gencache.EnsureDispatch("Word.Application")
        print("word openning")

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


# 删除文件以及对应的数据库内容
def fileremove(fileName):
    pdf_path = f"{file_path}/{fileName}.pdf"
    docx_path = f"{file_path}/{fileName}.docx"

    if os.path.exists(pdf_path):
        os.remove(pdf_path)
        print(pdf_path + "已删除")

    if os.path.exists(docx_path):
        os.remove(docx_path)
        print(docx_path + "已删除")


# 文件预览功能
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
        if lenSearchWord / lenWords >= 0.4:
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
    print("listW", listW)

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


# 保存文件
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


# 上传文件
@app.route("/fileUpload", methods=["POST"])
def file_upload():
    file = request.args.get("file")
    file_name = file.split(".")[1]
    file_name_ori = ""
    for i in range(len(file.split(".")) - 1):
        file_name_ori += file.split(".")[i]
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

    # # 等待文件创建完成
    for _ in range(30):  # 检查 30 次，每次等待 1 秒，总计 30 秒
        if os.path.exists(docx_path):
            print("docx exists")
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
                print("pdf not exists")
                # 执行文件转换
                convert_word_to_pdf(path, outpath)
            return response
        time.sleep(1)
    print("file err")
    return jsonify({"error": "File conversion timeout"}), 500

    # if os.path.exists(pdf_path):
    #     print("pdf exists")
    #     # pdf_blob = myTools.read_pdf_as_blob(pdf_path)
    #     # response = Response(io.BytesIO(pdf_blob), mimetype="application/pdf")
    #     # response.headers.set("Content-Disposition", "attachment", filename="sample.pdf")
    #     return response
    # else:
    #     # return send_file(f'{file_path}/{file}', as_attachment=True)
    #     # 执行文件转换
    #     convert_word_to_pdf(path, outpath)

    #     # # 等待文件创建完成
    #     for _ in range(30):  # 检查 30 次，每次等待 1 秒，总计 30 秒
    #         if os.path.exists(pdf_path):
    #             # pdf_blob = myTools.read_pdf_as_blob(pdf_path)
    #             # response = Response(io.BytesIO(pdf_blob), mimetype="application/pdf")
    #             # response.headers.set(
    #             #     "Content-Disposition", "attachment", filename="sample.pdf"
    #             # )
    #             docx_blob = myTools.read_pdf_as_blob(docx_path)
    #             response = Response(
    #                 io.BytesIO(docx_blob),
    #                 mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    #             )
    #             response.headers.set(
    #                 "Content-Disposition", "attachment", filename="sample.docx"
    #             )
    #             return response
    #         time.sleep(1)
    #     print("convert_to_pdf err")
    #     return jsonify({"error": "File conversion timeout"}), 500


# 分割
@app.route("/wordToSeq", methods=["POST"])
def word2seq():
    # 文件名
    file = request.json.get("file").split(".")[0] + ".docx"
    # 相邻两个chunk之间的重叠token数量
    overlap = request.json.get("overlap")
    # 最大分割长度
    chunkSize = request.json.get("chunkSize")
    # 分割的方法 0为递归 1为格式
    SplitType = request.json.get("SplitType")

    # 读取文件文字内容
    path = file_path + file
    word = myTools.read_word_file(path)
    # single_sentences_list = remove_newline_items(re.split(r'(?<=[。.?!\n\n])\s+', word))

    # sentences = [{'sentence': x, 'index': i} for i, x in enumerate(single_sentences_list)]
    # sentences = getSeq.RCSplit(word, chunkSize, overlap)
    sentences = []
    treeData = {}
    print(SplitType)
    if SplitType == 0:
        sentences = getSeq.RCSplit(word, chunkSize, overlap)
    else:
        sentences = getSeq.split_documentByOriChunk(file, word)
    return jsonify({"sentences": sentences, "treeData": treeData})


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
    # 先把原来的删除
    mg.del_data_db(collection_name, "fileName", fileName)
    # 再添加新的分词
    mg.insert_data(collection_name, textData)

    # 集合名称
    collection_name = "fileList"
    oriFileData = mg.updata_data_findone_db(
        collection_name, "fileName", fileName, {"chunkLen": len(textData)}
    )

    return jsonify(["success"])


@app.route("/loadtree", methods=["POST"])
def loadtree():
    textData = request.json.get("textData")
    res = c2t.getmind(textData)
    print(res)
    return jsonify(res)


"""
用户函数
"""


@app.route("/logincheck", methods=["POST"])
def logincheck():
    name = request.json.get("name")
    password = request.json.get("password")
    userdata = mg.fetch_user_data_db("user", "name", name)
    print(userdata)
    print(type(userdata))
    res = {}
    if userdata == {}:
        print("用户不存在")
        res = {"logindata": 1, "data": "用户不存在"}
    elif userdata["password"] != password:
        print("密码或用户名错误")
        res = {"logindata": 2, "data": "密码或用户名错误"}
    else:
        print("登录成功")
        res = {"logindata": 0, "data": "登陆成功"}
    return res


@app.route("/registcheck", methods=["POST"])
def registcheck():
    name = request.json.get("name")
    password = request.json.get("password")
    userdata = mg.fetch_user_data_db("user", "name", name)
    print(userdata)
    res = {}
    if userdata == {}:
        userdata = {
            "name": name,
            "password": password,
            "QAHistory": [
                {
                    "id": 1,
                    "isMe": False,
                    "quote": [],
                    "rawText": "你好,我有什么可以帮助你的吗？",
                    "text": "你好,我有什么可以帮助你的吗？",
                    "textWithQuote": [
                        {"quote": -1, "text": "你好,我有什么可以帮助你的吗？"}
                    ],
                }
            ],
        }
        mg.insert_data("user", [userdata])
        print("注册成功")
        res = {"logindata": 1, "data": "注册成功"}
    else:
        print("用户名已被占用")
        res = {"logindata": 0, "data": "注册失败"}
    return res


"""
回答索引匹配函数
"""


def remove_special_characters(strings):
    """
    处理掉列表中的特殊字符
    """
    special_characters = (
        "!@#$%^&*()_+{}[]|\:;'<>?,./\"，：；。？！、”“《》（）的了呢么吗\n请问我你他是 "
    )
    return [
        string
        for string in strings
        if not any(char in special_characters for char in string)
    ]


def ansSplit(ans):
    ansArr = ans.split("\n")
    # 将空的字符串去掉
    ansArr = list(filter(None, ansArr))

    # print("ansArr分割结果：", ansArr)
    return ansArr


def quoteMap(ans, quoteList):
    q = []
    for i in quoteList:
        q.append([ans, i["sentence"]])
    sorted_reScore = np.array(rerank.rerankerStore(q)).argsort()[::-1]

    return sorted_reScore[0]


def quotesMap(ansArr, quoteList):
    """
    将ansArr数组与quoteList数组对应起来
    """
    textWithQuote = []
    newQuoteList = []
    # 索引数组
    indexList = []
    index = 0
    nowNum = index
    print("quoteList", list(q["sentence"] for q in quoteList))

    for i in range(0, len(ansArr)):
        # 找到与ans最匹配的quote
        quoteNum = quoteMap(ansArr[i], quoteList)
        print("quoteNum:", quoteNum)
        # 如果是第一次出现的quoteNum
        if quoteNum not in indexList:
            indexList.append(quoteNum)
            nowNum = index
            index += 1
            newQuoteList.append(quoteList[int(quoteNum)])
        else:
            nowNum = indexList.index(quoteNum)

        textWithQuote.append({"text": str(ansArr[i]), "quote": nowNum})
    return (newQuoteList, textWithQuote)


"""
检索方法函数
"""


# 混合检索
def RRF(order1, order2, order3, holdValue):

    # 获取数据
    collection_name = "SeqVector"
    allData = mg.fetch_vectors_from_db(collection_name)

    Len1 = len(order1)
    Len2 = len(order2)
    Len3 = len(order3)
    score = [0.0] * len(allData)

    # RRF算法直接重排
    for i in range(0, Len1):
        score[order1[i]["order"]] += 1.0 / (i + 1)
    for i in range(0, Len2):
        score[order2[i]["order"]] += 1.0 / (i + 1)
    for i in range(0, Len3):
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
def reOrder(questions, quoutes):
    # 获取数据
    # collection_name = "SeqVector"
    # allData = mg.fetch_vectors_from_db(collection_name)

    q = []
    for i in quoutes:
        q.append([questions, i["sentence"]])
    sorted_reScore = np.array(rerank.rerankerStore(q)).argsort()[::-1]

    most_similar_data = []
    for index in sorted_reScore:
        vector_doc = quoutes[index]
        vector_doc["_id"] = str(vector_doc["_id"])
        # vector_doc["order"] = int(index)
        # vector_doc = mg.fetch_data_findone_db(collection_name,'index',int(index))
        most_similar_data.append(vector_doc)

    return most_similar_data


# 关键词检索
def keyWord(questions, holdValue):
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
    sorted_word = sorted_word[: 10 * holdValue]

    most_similar_data = []
    for index in sorted_word:
        vector_doc = allData[index]
        vector_doc["_id"] = str(vector_doc["_id"])
        vector_doc["order"] = int(index)
        # vector_doc = mg.fetch_data_findone_db(collection_name,'index',int(index))
        most_similar_data.append(vector_doc)

    return most_similar_data


# 余弦相似度检索
def wordVec(questions, holdValue):
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
    sorted_indices = sorted_indices[: 10 * holdValue]
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
def euDistance(questions, holdValue):
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
    sorted_euclidean_distance = sorted_euclidean_distance[: 10 * holdValue]

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
    user_input = (
        "你是一名文件数据管理人员，需要对用户的问题重新表达\n下面是用户的问题，请对其进行重新表述："
        + questions
    )
    # response_message = llmqa.zhipuChat(user_input)

    try:
        response_message = llmqa.zhipuChat(user_input)
        # response_message = llmqa.chatmodel(user_input)
        # response_message = generate_answer(user_input)
    except:
        # response_message = llmqa.zhipuChat(user_input)
        response_message = "err"

    # print("优化回答", response_message)
    return questions + "\n" + response_message


# 预回答
def preAnswer(questions):
    user_input = (
        "你是一名文件数据管理人员，需要对用户的问题精准的回答\n下面是用户的问题，请回答："
        + questions
    )
    # response_message = llmqa.zhipuChat(user_input)

    try:
        response_message = llmqa.zhipuChat(user_input)
        # response_message = llmqa.chatmodel(user_input)
        # response_message = generate_answer(user_input)
    except:
        # response_message = llmqa.zhipuChat(user_input)
        response_message = "err"
    # print("预回答：", response_message)
    return questions + "\n" + response_message


@app.route("/getFileList", methods=["GET"])
def getFileList():
    collection_name = "fileList"
    filiList = mg.fetch_alldata_db(collection_name)
    return jsonify(filiList)


@app.route("/getHistory", methods=["POST"])
def getHistory():
    print("getHistory")
    username = request.json.get("username")
    # print(username)
    # collection_name = "QAHistory"
    # filiList = mg.fetch_alldata_db(collection_name)
    userdata = mg.fetch_user_data_db("user", "name", username)
    fileList = []
    if userdata == None:
        print("帐户获取历史记录异常")
    else:
        fileList = userdata["QAHistory"]
    return jsonify(fileList)


@app.route("/saveHistory", methods=["POST"])
def saveHistory():
    print("saveHistory")
    mmr = request.json.get("history")
    username = request.json.get("username")
    # collection_name = "QAHistory"
    # mg.insert_data_clear(collection_name, mmr)
    orgindata = mg.fetch_user_data_db("user", "name", username)
    orgindata["QAHistory"] = mmr
    mg.updata_data_findone_db("user", "name", username, orgindata)
    return jsonify(["success"])
    # collection_name = "QAHistory"
    # filiList = mg.fetch_alldata_db(collection_name)
    # return jsonify(filiList)


@app.route("/getFileTextSeq", methods=["POST"])
def getFileTextSeq():
    """
    获得分割后存储在数据库的数据
    """
    fileName = request.json.get("fileName").split(".")[0]
    collection_name = "SeqVector"
    filiList = mg.fetch_data_find_db(collection_name, "fileName", fileName)
    return jsonify(filiList)


@app.route("/FileListDelOne", methods=["POST"])
def FileListDelOne():
    """
    删除文件
    """
    # 删除对应数据库数据
    fileName = request.json.get("fileName").split(".")[0]
    collection_nameS = "SeqVector"
    mg.del_data_db(collection_nameS, "fileName", fileName)
    print("语句分割已删除")
    collection_nameF = "fileList"
    mg.del_data_db(collection_nameF, "fileName", fileName)
    print("文件列表已删除")
    # 添加删除本地文件
    fileremove(fileName)

    # 返回删除后的文件列表
    filiList = mg.fetch_alldata_db(collection_nameF)
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

    answers = qap.pairQA(questions)
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
    quoteList = most_similar_data[:searchWeight]
    outKnowledge = ""

    # 问答准备
    if answers == "None":
        for q in quoteList:
            outKnowledge += q["sentence"]
        prompts = (
            "你是一名文件数据管理人员，需要对用户的问题根据资料精准得回答，如果资料中得不出结论，就不要回答，下面是相关的资料：\n"
            + outKnowledge
        )

        user_input = prompts + "下面是用户的问题，请回答：" + original_query

        print("问题长度：", len(user_input))
        # response_message = llmqa.zhipuChat(user_input)

        # 如果不能连上本地大模型就用zhipu模型
        try:
            response_message = llmqa.zhipuChat(user_input)
            # response_message = llmqa.chatmodel(user_input)
            # response_message = generate_answer(user_input)
        except:
            print("大模型出错")
            # response_message = llmqa.zhipuChat(user_input)
            response_message = "err"
        answers = str(response_message)

    # 对回答进行处理
    ansArr = ansSplit(answers)
    print("ansArr：", ansArr)
    time_start = time.time()  # 开始计时

    (newQuoteList, textWithQuote) = quotesMap(ansArr, quoteList)

    time_end = time.time()  # 结束计时
    time_c = time_end - time_start  # 运行所花时间
    print("index cost", time_c, "s")
    # -----------------------------------------------------------
    # else:
    #     newQuoteList = []
    #     textWithQuote = [{"text": answers, "quote": -1}]

    return jsonify(
        {
            "answers": answers,
            "quote": list(newQuoteList),
            "textWithQuote": list(textWithQuote),
        }
    )


# if __name__ == "__main__":
# app.run(debug=True, port=3000)

# 启动 Waitress 服务器
if __name__ == "__main__":
    if isWaitress:
        print("Waitress")
        serve(app, host="0.0.0.0", port=3000, threads=threads_num)
    else:
        print("flask")
        app.run(debug=True, port=3000)
