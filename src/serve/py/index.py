from flask import Flask, request, jsonify,make_response,send_file,Response
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

file_path = 'D:/Cailibuhong/Tobacco/py/data/杭烟营销中心各类标准文件/'

def convert_word_to_pdf(input_path, output_path):
    pythoncom.CoInitialize()
    # 创建Word应用程序实例
    pdf_file = os.path.join(output_path, os.path.splitext(os.path.basename(input_path))[0] + '.pdf')
    word_app = win32.gencache.EnsureDispatch('Word.Application')
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
    pdf_file = os.path.join(output_dir, os.path.splitext(os.path.basename(ofd_file))[0] + '.pdf')
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
        words = re.split(r'(?<=[  ，。。、.?!\n])', text)
        listW = myTools.remove_newline_items(words)
        print(listW)
        lenWords = len(words)
        lenSearchWord = 0
        for w in words:
            text_instances = page.search_for('第十四条')
            if text_instances:
                lenSearchWord +=1
        if lenSearchWord/lenWords >=0.8:
            return page_num+1   # 页码从 1 开始
    return 2

@app.route('/filePre', methods=['POST'])
def file_pre():
    file = request.args.get('file')
    text = request.args.get('text')
    outpath = file_path
    pdf_path = f'{outpath}/{file}.pdf'
    pdf_blob = myTools.read_pdf_as_blob(pdf_path)
    response = Response(io.BytesIO(pdf_blob), mimetype='application/pdf')
    response.headers.set('Content-Disposition', 'attachment', filename='sample.pdf')
    page = find_text_page_in_pdf(pdf_path, text)
    response.headers.set('PageNumber', page)
    print(page)
    return response
   

@app.route('/fileUpload', methods=['POST'])
def file_upload():
    file = request.args.get('file')
    file_name = file.split(".")[1]
    file_name_ori = file.split(".")[0]
    path = file_path+file
    outpath = file_path
    pdf_path = f'{outpath}/{file_name_ori}.pdf'
    if os.path.exists(pdf_path):
        pdf_blob = myTools.read_pdf_as_blob(pdf_path)
        response = Response(io.BytesIO(pdf_blob), mimetype='application/pdf')
        response.headers.set('Content-Disposition', 'attachment', filename='sample.pdf')
        return response
    else:
            # return send_file(f'{file_path}/{file}', as_attachment=True)
        # 执行文件转换
        convert_word_to_pdf(path, outpath)

        # # 等待文件创建完成
        for _ in range(30):  # 检查 30 次，每次等待 1 秒，总计 30 秒
            if os.path.exists(pdf_path):
                pdf_blob = myTools.read_pdf_as_blob(pdf_path)
                response = Response(io.BytesIO(pdf_blob), mimetype='application/pdf')
                response.headers.set('Content-Disposition', 'attachment', filename='sample.pdf')
                return response
            time.sleep(1)

        return jsonify({'error': 'File conversion timeout'}), 500

    

@app.route('/wordToSeq', methods=['POST'])
def word2seq():
    file = request.json.get('file')    
    overlap = request.json.get('overlap')
    chunkSize = request.json.get('chunkSize')
    path = file_path+file
    word = myTools.read_word_file(path)
    # single_sentences_list = remove_newline_items(re.split(r'(?<=[。.?!\n\n])\s+', word))

    # sentences = [{'sentence': x, 'index': i} for i, x in enumerate(single_sentences_list)]
    sentences = getSeq.RCSplit(word,chunkSize,overlap)
    return jsonify(sentences)


@app.route('/seqToVec', methods=['POST'])
def seq2vec():
    textData = request.json.get('textData')   
    fileName = request.json.get('fileName') .split(".")[0]
    embeddings = sentence2Vec.embedding_generate([x['sentence'] for x in textData])
    for i, sentence in enumerate(textData):
        sentence['fileName'] = str(fileName)
        sentence['sentence_embedding'] = str([x for x in embeddings[i]])
    # 集合名称
    collection_name = 'SeqVector'
    mg.insert_data(collection_name, textData)
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
    similarities = cosine_similarity(vector_array, target_vector.reshape(1, -1)).flatten()
    
    # 获取最相似的前 top_n 个向量的索引
    most_similar_indices = similarities.argsort()[-top_n:][::-1]
    
    # 返回最相似向量的索引及其相似度
    most_similar_vectors = [(index, similarities[index]) for index in most_similar_indices]
    return most_similar_vectors



def main():
    # 从 MongoDB 中检索向量数据
    collection_name = 'SeqVector'
    vector_data = mg.fetch_vectors_from_db(collection_name)
    
    # # 将向量数据转换为 numpy 数组
    # vector_array = np.array(vector_data)
    
    # # 示例目标向量
    # target_vector = np.array([1.0, 1.0, 0.5])
    
    # # 查找最相似的前 3 个向量
    # most_similar = find_most_similar_vectors(vector_array, target_vector, top_n=3)
    
    # # 从 MongoDB 中返回最相似向量的具体数据
    # most_similar_data = []
    # for index, similarity in most_similar:
    #     vector_doc = collection.find_one({'vector': vector_data[index]})
    #     vector_doc['similarity'] = similarity
    #     most_similar_data.append(vector_doc)
    
    # print("Most similar vectors:")
    # for data in most_similar_data:
    #     print(data)


@app.route('/QA', methods=['POST'])
def QandA():
    questions = request.json.get('questions')    
    print(questions)
    queVec = sentence2Vec.embedding_generate(questions)
    
    collection_name = 'SeqVector'
    allData = mg.fetch_vectors_from_db(collection_name)
    vector_data = [ast.literal_eval(doc['sentence_embedding']) for doc in allData]
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
    
    outKnowledge = ''
    for da in most_similar_data:
        outKnowledge += da['sentence']
    messages = []
    # client = ZhipuAI(api_key="ca48767be5d0dbc41b3a135f7be786da.w5O4CRLo111zUlbj")  # 填写您自己的APIKey

    prompts = '你是一名烟草公司的数据管理人员，需要对用户的问题精准得回答，下面是你的资料：\n'+outKnowledge
    
    user_input = prompts+"下面是用户的问题，请回答："+questions
    print(user_input)
    answers = '11'
    print(type(most_similar_data))
    # -----------------------------------------------------------
    # messages += [{"role": "user", "content": user_input}]
    # response = client.chat.completions.create(
    #     model="glm-4",  # 填写需要调用的模型名称
    #     messages=messages
    # )
    # response_message = response.choices[0].message.content
    # answers = str(response_message)
    # -----------------------------------------------------------
    return jsonify({"answers":answers,"quote":list(most_similar_data)})

if __name__ == "__main__":
    app.run(debug=True,port=3000)

