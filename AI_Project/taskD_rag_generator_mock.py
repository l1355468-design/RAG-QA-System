# -*- coding: utf-8 -*-
"""成员D：RAG问答生成模块 - 模拟版（不依赖真实API）"""

from taskC_hybrid_retriever import HybridRetriever

class RAGGenerator:
    def __init__(self, data_dir, api_key=None, base_url=None):
        self.retriever = HybridRetriever(data_dir)
        print("✅ RAG生成器初始化完成（模拟模式）")

    def generate(self, query, top_k=3, alpha=0.5):
        # 1. 检索相关文档
        retrieved_chunks = self.retriever.retrieve(query, top_k=top_k, alpha=alpha)

        if not retrieved_chunks:
            return {"answer": "没有找到与您问题相关的资料。", "sources": []}

        # 2. 基于检索结果“模拟”生成专业答案
        sources_info = []
        context_list = []
        for i, chunk in enumerate(retrieved_chunks):
            context_list.append(f"【参考文档{i+1}片段】：{chunk['text'][:150]}...")
            sources_info.append({
                "source_file": chunk['source_file'],
                "text_preview": chunk['text'][:100] + "...",
                "score": chunk['score']
            })

        # 模拟LLM组织答案
        answer = f"根据检索到的资料，关于「{query}」的相关信息如下：\n\n"
        answer += "\n".join(context_list)
        answer += "\n\n（此为基于检索结果的模拟回答，正式接入大模型后可生成更精炼的答案。）"

        return {"answer": answer, "sources": sources_info}

    def chat(self, query):
        result = self.generate(query)
        output = result["answer"]
        if result["sources"]:
            output += "\n\n📚 **参考来源**：\n"
            for i, s in enumerate(result["sources"]):
                output += f"{i+1}. {s['source_file']} (相关度: {s['score']:.3f})\n"
        return output

# 测试代码
if __name__ == "__main__":
    rag = RAGGenerator(r"C:\AI_Project\data\processed")
    test_q = "什么是信息检索？"
    print(f"\n用户: {test_q}")
    print(f"助手: {rag.chat(test_q)}")