# -*- coding: utf-8 -*-
"""
Created on Sun May 17 10:21:58 2026

@author: 焱
"""

import json
import os

# 文件路径
input_path = r"C:\AI_Project\data\processed\documents.jsonl"
output_dir = r"C:\AI_Project\data\processed"
os.makedirs(output_dir, exist_ok=True)

# 读取JSONL文件
documents = []
with open(input_path, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            documents.append(json.loads(line))

print(f"成功读取 {len(documents)} 条文档")


import re

def clean_text(text):
    """清洗文本：去多余空格、特殊字符、链接"""
    # 去除链接
    text = re.sub(r'https?://\S+', '', text)
    # 去除多余换行和空格
    text = re.sub(r'\s+', ' ', text)
    # 去除特殊符号（保留中文、英文、数字、常用标点）
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\。\，\？\！\；\：\“\”\‘\’\（\）]', ' ', text)
    # 去除首尾空格
    text = text.strip()
    return text

# 清洗所有文档的content字段
for doc in documents:
    if 'content' in doc:
        doc['content_cleaned'] = clean_text(doc['content'])

print("文本清洗完成")


from tqdm import tqdm

def split_text(text, max_length=250, overlap=50):
    """按句子切分文本，每个chunk约max_length字符，保留overlap重叠"""
    if len(text) <= max_length:
        return [text]
    
    # 按句号、问号、感叹号切分
    sentences = re.split(r'([。！？])', text)
    # 重组（保留标点符号）
    sentences = [sentences[i] + (sentences[i+1] if i+1 < len(sentences) else '') 
                 for i in range(0, len(sentences), 2)]
    
    chunks = []
    current_chunk = ""
    for sent in sentences:
        if len(current_chunk) + len(sent) <= max_length:
            current_chunk += sent
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # 重叠：保留当前chunk最后overlap个字符
            if overlap > 0 and len(current_chunk) > overlap:
                current_chunk = current_chunk[-overlap:] + sent
            else:
                current_chunk = sent
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

# 对所有文档进行分块
all_chunks = []
chunk_id = 0

for doc in tqdm(documents, desc="分块处理"):
    text = doc.get('content_cleaned', '')
    if not text:
        continue
    
    chunks = split_text(text, max_length=250, overlap=50)
    
    for chunk in chunks:
        all_chunks.append({
            "chunk_id": chunk_id,
            "text": chunk,
            "source_doc_id": doc.get('id', 'unknown'),
            "source_file": doc.get('source', 'unknown'),
            "original_title": doc.get('title', '')
        })
        chunk_id += 1

print(f"共生成 {len(all_chunks)} 个文本块")

# 保存chunks
chunks_path = os.path.join(output_dir, "chunks.json")
with open(chunks_path, 'w', encoding='utf-8') as f:
    json.dump(all_chunks, f, ensure_ascii=False, indent=2)
print(f"Chunks已保存至: {chunks_path}")


from sentence_transformers import SentenceTransformer
import numpy as np

# 加载中文嵌入模型（使用BGE小模型，CPU也能运行）
print("正在加载嵌入模型...")
model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
print("模型加载完成")

# 提取所有chunk的文本
chunk_texts = [chunk['text'] for chunk in all_chunks]

# 生成向量（归一化，方便内积计算）
print("正在生成向量，可能需要几分钟...")
embeddings = model.encode(chunk_texts, normalize_embeddings=True, show_progress_bar=True)
print(f"向量生成完成，形状: {embeddings.shape}")


import faiss

# 获取向量维度
dimension = embeddings.shape[1]

# 创建FAISS索引（使用内积，即余弦相似度）
index = faiss.IndexFlatIP(dimension)

# 添加向量到索引
index.add(embeddings.astype('float32'))
print(f"FAISS索引构建完成，包含 {index.ntotal} 个向量")

# 保存FAISS索引
index_path = os.path.join(output_dir, "faiss_index.bin")
faiss.write_index(index, index_path)
print(f"FAISS索引已保存至: {index_path}")

# 保存向量（可选，用于调试）
vectors_path = os.path.join(output_dir, "embeddings.npy")
np.save(vectors_path, embeddings)
print(f"向量已保存至: {vectors_path}")



# 保存chunks（带向量索引位置信息）
chunks_with_metadata = []
for i, chunk in enumerate(all_chunks):
    chunks_with_metadata.append({
        "index": i,  # 对应FAISS中的位置
        "chunk_id": chunk['chunk_id'],
        "text": chunk['text'],
        "source_doc_id": chunk['source_doc_id'],
        "source_file": chunk['source_file'],
        "original_title": chunk['original_title']
    })

metadata_path = os.path.join(output_dir, "chunks_with_metadata.json")
with open(metadata_path, 'w', encoding='utf-8') as f:
    json.dump(chunks_with_metadata, f, ensure_ascii=False, indent=2)
print(f"带元数据的chunks已保存至: {metadata_path}")

def search(query, top_k=5):
    """测试检索功能"""
    query_vec = model.encode([query], normalize_embeddings=True)
    distances, indices = index.search(query_vec.astype('float32'), top_k)
    
    results = []
    for i, idx in enumerate(indices[0]):
        if idx != -1:
            results.append({
                "score": float(distances[0][i]),
                "text": chunks_with_metadata[idx]['text'],
                "source": chunks_with_metadata[idx]['source_file']
            })
    return results

# 测试
test_query = "什么是信息检索"
results = search(test_query)
print(f"\n查询: {test_query}")
print("检索结果:")
for r in results:
    print(f"  [得分:{r['score']:.4f}] {r['text'][:100]}...")
    
    
    
