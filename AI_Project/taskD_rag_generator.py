# -*- coding: utf-8 -*-
"""成员D：RAG问答生成模块 - 使用你的自定义网关"""

from taskC_hybrid_retriever import HybridRetriever
from openai import OpenAI


class RAGGenerator:
    
    def __init__(self, data_dir, api_key, base_url):
        """
        data_dir: 数据目录
        api_key: 你的 API Key
        base_url: 你的网关地址（compatible-mode/v1）
        """
        self.retriever = HybridRetriever(data_dir)
        
        # 使用你的自定义网关
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = "qwen-turbo"  # 或者 qwen-plus, qwen-max
        print("✅ RAG生成器初始化完成")
    
    def build_prompt(self, query, retrieved_chunks):
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks):
            context_parts.append(f"【参考文档{i+1}】\n{chunk['text']}")
        context = "\n\n".join(context_parts)
        
        system_prompt = """你是一个专业的知识问答助手。请根据以下【参考文档】回答用户的问题。

要求：
1. 答案必须基于参考文档的内容，不要编造信息
2. 如果参考文档中没有相关信息，请回答"根据现有资料无法回答这个问题"
3. 在答案末尾，用[来源：文档X]的形式标注引用
4. 回答要简洁、准确、有条理
5. 使用中文回答"""

        user_prompt = f"""【参考文档】
{context}

【用户问题】
{query}

【回答】"""
        
        return system_prompt, user_prompt
    
    def generate(self, query, top_k=3, alpha=0.5):
        # 1. 检索
        retrieved_chunks = self.retriever.retrieve(query, top_k=top_k, alpha=alpha)
        
        if not retrieved_chunks:
            return {
                "answer": "没有找到与您问题相关的资料，请尝试换个问法。",
                "sources": [],
                "retrieved_chunks": []
            }
        
        # 2. 构建Prompt
        system_prompt, user_prompt = self.build_prompt(query, retrieved_chunks)
        
        # 3. 调用LLM
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"调用大模型时出错：{str(e)}"
        
        # 4. 提取来源
        sources = []
        for chunk in retrieved_chunks:
            sources.append({
                "source_file": chunk['source_file'],
                "text_preview": chunk['text'][:100] + "...",
                "score": chunk['score']
            })
        
        return {
            "answer": answer,
            "sources": sources,
            "retrieved_chunks": retrieved_chunks
        }
    
    def chat(self, query):
        result = self.generate(query)
        output = result["answer"]
        
        if result["sources"]:
            output += "\n\n📚 **参考来源**：\n"
            for i, src in enumerate(result["sources"]):
                output += f"{i+1}. {src['source_file']}\n"
        
        return output


# ========== 测试代码 ==========
if __name__ == "__main__":
    DATA_DIR = r"C:\AI_Project\data\processed"
    
    # 使用你提供的配置
    API_KEY = "sk-ca36500a121148719af2ec014993c5ce"
    BASE_URL = "https://ws-tuzy4hqctx3z1wvz.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
    
    rag = RAGGenerator(DATA_DIR, API_KEY, BASE_URL)
    
    test_queries = [
        "什么是信息检索？",
        "推荐系统有哪些常用的算法？",
        "知识图谱可以用来做什么？"
    ]
    
    print("\n" + "="*70)
    print("RAG问答系统测试")
    print("="*70)
    
    for query in test_queries:
        print(f"\n📝 用户问题: {query}")
        print("-" * 50)
        
        result = rag.generate(query, top_k=3, alpha=0.5)
        
        print(f"🤖 回答:\n{result['answer']}")
        print(f"\n📂 引用来源:")
        for src in result['sources']:
            print(f"   - {src['source_file']} (得分:{src['score']:.3f})")
        print("-" * 50)