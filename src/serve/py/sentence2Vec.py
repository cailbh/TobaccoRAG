import torch
from sentence_transformers import SentenceTransformer


# 检查是否有可用的CUDA设备
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# 加载模型并将其移动到指定设备
model = SentenceTransformer(r".\bge-large-zh-v1.5", device=device)

def embedding_generate(word):
    embedding = model.encode(word, normalize_embeddings=True, device=device)
    return embedding