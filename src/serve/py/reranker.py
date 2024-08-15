from FlagEmbedding import FlagReranker
import json

reranker_path = "../models/bge-reranker-base"

# 读取json文件
with open("./config.json", "r") as f:
    data = json.load(f)
    reranker_path = data["reranker_path"]

reranker = FlagReranker(
    reranker_path, use_fp16=True
)  # Setting use_fp16 to True speeds up computation with a slight performance degradation
# reranker = FlagReranker(
#     "./bge-reranker-base", use_fp16=True
# )  # Setting use_fp16 to True speeds up computation with a slight performance degradation


# scores = reranker.compute_score([['what is panda?', 'hi'], ['what is panda?', 'The giant panda (Ailuropoda melanoleuca), sometimes called a panda bear or simply panda, is a bear species endemic to China.']])
def rerankerStore(query):
    score = reranker.compute_score(query)
    return score
