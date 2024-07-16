import jieba
import sys
from pymongo import MongoClient
import numpy as np
import jieba.analyse

client = MongoClient('mongodb://127.0.0.1:27017')
db = client.FMS
mycol = db['project']
jieba.load_userdict("D:\Cailibuhong\XGD\kg4payoffs\src\serve/py/wordDict.txt")
jieba.initialize()

stop_words = set()
with open('D:\Cailibuhong\XGD\kg4payoffs\src\serve/py/stop_words.txt', encoding='utf-8') as f: 
    con = f.readlines()
    for i in con:
        i = i.replace("\n", "")   # 去掉读取每一行数据的\n
        stop_words.add(i)

def main(field):
    # myquery = {"id": "this"}
    doc = mycol.find()
    wordList = []
    words = ''
    for d in doc:
        words += d[field]
    seg_list = jieba.cut(words)
    # seg_list =jieba.cut_for_search(words)

    wordList = []
    for word in seg_list:
        if word not in stop_words and len(word) > 1:
            wordList.append(word)      


    Colos = [[1, 2, 3,4,5,6,7]]  # 示例数据

    sizeDomin = [5, 20]
    wordNumDomin = [100000, 0]
    wordMap = {}
    wIndx = 0

    for w in wordList:
        if w not in wordMap:
            wordMap[w] = [0, wIndx]
            wIndx += 1
            wIndx %= len(Colos[0])
        wordMap[w][0] += 1
        wordNumDomin[0] = min(wordMap[w][0], wordNumDomin[0])
        wordNumDomin[1] = max(wordMap[w][0], wordNumDomin[1])

    # 对 wordMap 按词频进行排序，取前30个词频最高的词
    sorted_word_map = sorted(wordMap.items(), key=lambda item: item[1][0], reverse=True)[:30]

    # 重新构建 wordMap 只保留前30个词
    wordMap = {k: v for k, v in sorted_word_map}

    # 创建线性比例尺
    wordSizeScale = np.interp([v[0] for v in wordMap.values()], wordNumDomin, sizeDomin)

    # 构建 wordList
    wordList = [[word, wordSizeScale[idx]] for idx, (word, v) in enumerate(wordMap.items())]

    print({"wordList": wordList,"wordMap": wordMap})


if __name__ == '__main__':
    # print(["你好"])
    main(sys.argv[1])
