import torch
from sentence_transformers import SentenceTransformer
import json
import numpy as np
from bson.binary import Binary

sentence2Vec_path = r"../models/bge-large-zh-v1.5"

# 读取json文件
with open("./config.json", "r") as f:
    data = json.load(f)
    sentence2Vec_path = data["sentence2Vec_path"]

# 检查是否有可用的CUDA设备
device = "cuda" if torch.cuda.is_available() else "cpu"

# 加载模型并将其移动到指定设备
model = SentenceTransformer(sentence2Vec_path, device=device)


def embedding_generate(word):
    embedding = model.encode(word, normalize_embeddings=True, device=device)
    return embedding


# 处理向量存储
def from_binary(binary_data, shape, dtype):
    # tuple(shape)
    shape = list(shape)
    return np.frombuffer(binary_data, dtype=np.dtype(dtype)).reshape(shape)


def to_binary(array):
    return Binary(array.tobytes()), array.shape, str(array.dtype)
