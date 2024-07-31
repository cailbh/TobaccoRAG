from flask import Flask, request, jsonify, make_response, send_file, Response
from flask_cors import CORS
import os
import io
import re
import subprocess
import time
import fitz  # PyMuPDF
import win32com.client as win32

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

file_path = 'D:\Work\YanCao\TobaccoRAG\data/杭烟营销中心各类标准文件/'

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
    return 0


def find_text_in_pdf(pdf_path, page_num, text):
    """
    在 PDF 文件的指定页面中查找文字并返回矩形块
    """
    document = fitz.open(pdf_path)
    # 检查页面号是否有效
    if page_num < 1 or page_num > len(document):
        return -1

    page = document.load_page(page_num - 1)
    words = re.split(r"(?<=[  ，。。、.?!\n])", text)
    res = []
    for w in words:
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
    pdf_path = f"{outpath}/{file}.pdf"
    pdf_blob = myTools.read_pdf_as_blob(pdf_path)
    response = Response(io.BytesIO(pdf_blob), mimetype="application/pdf")
    response.headers.set("Content-Disposition", "attachment", filename="sample.pdf")
    page = find_text_page_in_pdf(pdf_path, text)
    response.headers.set("PageNumber", page)
    print(page)
    pagerects = find_text_in_pdf(pdf_path, page, text)
    response.headers.set("PageRects", pagerects)
    return response


@app.route("/fileUpload", methods=["POST"])
def file_upload():
    file = request.args.get("file")
    file_name = file.split(".")[1]
    file_name_ori = file.split(".")[0]
    path = file_path + file
    outpath = file_path
    pdf_path = f"{outpath}/{file_name_ori}.pdf"

    # 集合名称
    collection_name = 'fileList'
    oriFileData = mg.fetch_data_findone_db(collection_name,"fileName",file_name_ori)
    print(collection_name,"fileName",file_name_ori,oriFileData)
    if (oriFileData == None) | (oriFileData == []):
        mg.insert_data(collection_name, [{"fileName":file_name_ori}])

    if os.path.exists(pdf_path):
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
    file = request.json.get("file")
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
    collection_name = 'fileList'
    oriFileData = mg.updata_data_findone_db(collection_name,"fileName",fileName,{'chunkLen':len(textData)})

    return jsonify(['success'])




def find_most_similar_vectors(vector_array, target_vector, top_n=5):
    """
    在向量数组中查找与目标向量最相似的前几个向量

    :param vector_array: np.ndarray, 向量数组，形状为 (num_vectors, vector_dim)
    :param target_vector: np.ndarray, 目标向量，形状为 (vector_dim,)
    :param top_n: int, 要查找的最相似向量的数量
    :return: list, 最相似向量的索引及其相似度
    """
    # 计算目标向量与向量数组中每个向量的余弦相似度
    similarities = cosine_similarity(
        vector_array, target_vector.reshape(1, -1)
    ).flatten()

    # 获取最相似的前 top_n 个向量的索引
    most_similar_indices = similarities.argsort()[-top_n:][::-1]

    # 返回最相似向量的索引及其相似度
    most_similar_vectors = [
        (index, similarities[index]) for index in most_similar_indices
    ]
    return most_similar_vectors


@app.route("/getFileList", methods=["GET"])
def getFileList():
    collection_name = "fileList"
    filiList = mg.fetch_alldata_db(collection_name)
    return jsonify(filiList)


@app.route("/getFileTextSeq", methods=["POST"])
def getFileTextSeq():
    fileName = request.json.get("fileName").split(".")[0]
    collection_name = "SeqVector"
    filiList = mg.fetch_data_find_db(collection_name, "fileName", fileName)
    return jsonify(filiList)


@app.route("/QA", methods=["POST"])
def QandA():
    questions = request.json.get("questions")
    print(questions)
    queVec = sentence2Vec.embedding_generate(questions)

    collection_name = "SeqVector"
    allData = mg.fetch_vectors_from_db(collection_name)
    vector_data = [ast.literal_eval(doc["sentence_embedding"]) for doc in allData]
    # # 将向量数据转换为 numpy 数组
    vector_array = np.array(vector_data)
    target_vector = np.array(queVec)
    most_similar = find_most_similar_vectors(vector_array, target_vector, top_n=3)

    most_similar_data = []
    for index, similarity in most_similar:
        vector_doc = allData[index]
        vector_doc["_id"] = str(vector_doc["_id"])
        # vector_doc = mg.fetch_data_findone_db(collection_name,'index',int(index))
        most_similar_data.append(vector_doc)

    outKnowledge = ""
    for da in most_similar_data:
        outKnowledge += da["sentence"]
    messages = []
    client = ZhipuAI(
        api_key="ca48767be5d0dbc41b3a135f7be786da.w5O4CRLo111zUlbj"
    )  # 填写您自己的APIKey

    prompts = (
        "你是一名烟草公司的数据管理人员，需要对用户的问题精准得回答，下面是你的资料：\n"
        + outKnowledge
    )

    user_input = prompts + "下面是用户的问题，请回答：" + questions
    print(user_input)
    answers = ''
    # answers = "卷烟货源供应方式在提供的资料中没有直接说明，但可以根据常规的商业操作推断，卷烟货源供应通常有以下几种方式：1. **直接供应**：烟草公司直接向零售客户供应卷烟，这通常涉及配送中心发放促销品给零售商，如资料中第十九条所述，依据审批程序和《卷烟促销品领用单》进行。2. **分销网络供应**：通过建立分销网络，烟草公司可以通过分销商或批发商向零售商供应卷烟。3. **电商平台供应**：随着技术的发展，烟草公司也可能通过官方电商平台或合作第三方电商平台，如资料中提到的“香溢家”APP，进行线上供应。4. **库存管理供应**：烟草公司会定期对促销品进行盘库，如资料中第二十条所述，确保库存与帐目相符，从而有效管理货源供应。在供应过程中，烟草公司会考虑到促销活动的类型（如品规培育性活动或退市卸库性活动），合理安排货源，以满足市场需求，同时确保促销活动的合规性。促销活动的具体方式包括线上促销和线下促销，这些活动都会对货源供应产生影响。若需要具体了解卷烟货源供应的详细信息，建议参考烟草公司提供的具体操作手册或直接咨询烟草公司的相关部门。"
    print(type(most_similar_data))
    # -----------------------------------------------------------
    messages += [{"role": "user", "content": user_input}]
    response = client.chat.completions.create(
        model="glm-4", messages=messages  # 填写需要调用的模型名称
    )
    response_message = response.choices[0].message.content
    answers = str(response_message)
    # -----------------------------------------------------------
    return jsonify({"answers": answers, "quote": list(most_similar_data)})


if __name__ == "__main__":
    app.run(debug=True, port=3000)
