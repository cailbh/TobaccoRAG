from pymongo import MongoClient


uri = 'mongodb://localhost:27017/'
# 数据库名称
db_name = 'Tobacco'
# 集合名称
collection_name = 'SeqVector'


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

def fetch_data_findone_db(collectionName,key,value):
     # 获取集合
    collection = db[collectionName]
    data = collection.find_one({key: value})
    return data

def insert_data(collection_name, data):
    # 获取集合
    collection = db[collection_name]
    # # 清空集合
    # collection.delete_many({})
    # 插入数据
    result = collection.insert_many(data)
    return result.inserted_ids