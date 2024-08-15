from pymongo import MongoClient
import json


uri = "mongodb://localhost:27017/"
# 数据库名称
db_name = "Tobacco"
# 集合名称
collection_name = "SeqVector"
# 读取json文件
with open("./config.json", "r") as f:
    data = json.load(f)
    uri = data["mongodb_url"]
    db_name = data["db_name"]
    collection_name = data["collection_name"]


def connect_to_mongo(uri, db_name):
    # 连接到MongoDB
    client = MongoClient(uri)
    db = client[db_name]
    return db


# 连接到MongoDB
db = connect_to_mongo(uri, db_name)


def fetch_vectors_from_db(collectionName):
    """
    从 MongoDB 中检索向量数据

    :param collection: pymongo.collection.Collection, MongoDB 集合
    :return: list, 包含所有向量的列表
    """
    # 获取集合
    collection = db[collectionName]
    cursor = collection.find()
    vectors = [doc for doc in cursor]
    return vectors


def fetch_data_findone_db(collectionName, key, value):
    # 获取集合
    collection = db[collectionName]
    data = collection.find_one({key: value})
    res = []
    if data != None:
        res = [doc for doc in data]
    return res


def del_data_db(collectionName, key, value):
    # 获取集合
    collection = db[collectionName]
    data = collection.delete_many({key: value})
    return


def updata_data_findone_db(collectionName, key, value, news):
    # 获取集合
    collection = db[collectionName]
    myquery = {key: value}
    newvalues = {"$set": news}

    collection.update_one(myquery, newvalues)
    return "success"


def fetch_data_find_db(collectionName, key, value):
    # 获取集合
    collection = db[collectionName]
    data = collection.find({key: value})
    res = []
    if data != None:
        for doc in data:
            doc["_id"] = str("_id")
            res.append(doc)
    return res


def fetch_alldata_db(collectionName):
    # 获取集合
    collection = db[collectionName]
    data = collection.find({}, {"_id": 0})
    res = []
    if data != None:
        res = [doc for doc in data]
    return res


def insert_data(collection_name, data):
    # 获取集合
    collection = db[collection_name]
    # # 清空集合
    # collection.delete_many({})
    # 插入数据
    result = collection.insert_many(data)
    return result.inserted_ids


def insert_data_clear(collection_name, data):
    # 获取集合
    collection = db[collection_name]
    # # 清空集合
    collection.delete_many({})
    # 插入数据
    result = collection.insert_many(data)
    return result.inserted_ids
