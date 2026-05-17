# -*- coding: utf-8 -*-
"""
成员C：混合检索模块（稠密检索 + BM25稀疏检索）
"""

import json
import os
import numpy as np
import faiss
import jieba
from rank_bm25 import BM25Okapi

class HybridRetriever:
    """
    混合检索器：融合FAISS稠密检索和BM25稀疏检索
    """
    
    def __init__(self, data_dir):
        """
        初始化检索器，加载FAISS索引和chunks
        data_dir: 数据目录，如 C:\AI_Project\data\processed
        """
        self.data_dir = data_dir
        
        # 1. 加载chunks_with_metadata
        chunks_path = os.path.join(data_dir, "chunks_with_metadata.json")
        with open(chunks_path, 'r', encoding='utf-8') as f:
            self.chunks = json.load(f)
        print(f"✅ 加载 {len(self.chunks)} 个文本块")
        
        # 2. 加载FAISS索引
        index_path = os.path.join(data_dir, "faiss_index.bin")
        self.index = faiss.read_index(index_path)
        print(f"✅ 加载FAISS索引，包含 {self.index.ntotal} 个向量")
        
        # 3. 准备BM25索引（需要分词）
        print("正在构建BM25索引（分词中）...")
        tokenized_chunks = []
        for chunk in self.chunks:
            # 对每个chunk的文本进行分词
            tokens = list(jieba.cut(chunk['text']))
            # 过滤掉单字符和停用词（可选）
            tokens = [t for t in tokens if len(t) > 1]
            tokenized_chunks.append(tokens)
        
        self.bm25 = BM25Okapi(tokenized_chunks)
        print(f"✅ BM25索引构建完成")
        
        # 4. 加载嵌入模型（用于查询向量化）
        from sentence_transformers import SentenceTransformer
        self.embed_model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
        print(f"✅ 嵌入模型加载完成")
    
    def dense_search(self, query, top_k=10):
        """
        稠密检索：使用FAISS
        返回: list of (chunk_index, score)
        """
        # 将查询向量化
        query_vec = self.embed_model.encode([query], normalize_embeddings=True)
        
        # FAISS检索
        distances, indices = self.index.search(query_vec.astype('float32'), top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:
                results.append((int(idx), float(distances[0][i])))
        return results
    
    def sparse_search(self, query, top_k=10):
        """
        稀疏检索：使用BM25
        返回: list of (chunk_index, score)
        """
        # 对查询分词
        query_tokens = list(jieba.cut(query))
        query_tokens = [t for t in query_tokens if len(t) > 1]
        
        # BM25计算得分
        scores = self.bm25.get_scores(query_tokens)
        
        # 获取top_k的索引
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append((int(idx), float(scores[idx])))
        return results
    
    def hybrid_search(self, query, top_k=5, alpha=0.5):
        """
        混合检索：融合稠密检索和稀疏检索
        alpha: 稠密检索的权重 (0~1)，稀疏检索权重为 1-alpha
        返回: list of (chunk_index, combined_score, chunk_dict)
        """
        # 获取两种检索结果（取更多候选，用于融合）
        dense_results = self.dense_search(query, top_k=top_k*2)
        sparse_results = self.sparse_search(query, top_k=top_k*2)
        
        # 归一化得分
        def normalize(results):
            if not results:
                return []
            scores = [r[1] for r in results]
            max_score = max(scores)
            min_score = min(scores)
            if max_score == min_score:
                return [(r[0], 1.0) for r in results]
            return [(r[0], (r[1] - min_score) / (max_score - min_score)) for r in results]
        
        dense_norm = normalize(dense_results)
        sparse_norm = normalize(sparse_results)
        
        # 融合得分
        combined = {}
        for idx, score in dense_norm:
            combined[idx] = alpha * score
        for idx, score in sparse_norm:
            combined[idx] = combined.get(idx, 0) + (1 - alpha) * score
        
        # 排序并取top_k
        sorted_idx = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        # 返回结果（包含chunk详细信息）
        results = []
        for idx, score in sorted_idx:
            results.append({
                "index": idx,
                "score": score,
                "chunk_id": self.chunks[idx]['chunk_id'],
                "text": self.chunks[idx]['text'],
                "source_file": self.chunks[idx]['source_file'],
                "original_title": self.chunks[idx]['original_title']
            })
        return results
    
    def retrieve(self, query, top_k=5, alpha=0.5):
        """
        对外接口：返回检索结果（供成员D调用）
        """
        return self.hybrid_search(query, top_k=top_k, alpha=alpha)


# ========== 测试代码 ==========
if __name__ == "__main__":
    # 初始化检索器
    data_dir = r"C:\AI_Project\data\processed"
    retriever = HybridRetriever(data_dir)
    
    # 测试查询
    test_queries = [
        "什么是信息检索",
        "推荐系统有哪些算法",
        "知识图谱有什么用"
    ]
    
    print("\n" + "="*60)
    print("混合检索测试（alpha=0.5，稠密和稀疏各占一半）")
    print("="*60)
    
    for query in test_queries:
        print(f"\n📝 查询: {query}")
        results = retriever.retrieve(query, top_k=3, alpha=0.5)
        
        print("检索结果:")
        for i, r in enumerate(results):
            print(f"  {i+1}. [得分:{r['score']:.4f}] {r['text'][:80]}...")
            print(f"     来源: {r['source_file']}")