"""RAG智能问答系统 - 主入口"""
import sys
import os

sys.path.append(r"C:\AI_Project")

from taskD_rag_generator_mock import RAGGenerator
import gradio as gr

def main():
    print("="*50)
    print("🚀 RAG智能问答系统启动中...")
    print("="*50)
    
    data_dir = r"C:\AI_Project\data\processed"

    
    rag = RAGGenerator(data_dir)
    
    def chat(message, history):
        result = rag.generate(message, top_k=3, alpha=0.5)
        answer = result["answer"]
        if result["sources"]:
            answer += "\n\n📚 **参考来源**：\n"
            for i, s in enumerate(result["sources"]):
                answer += f"{i+1}. {s['source_file']} (得分:{s['score']:.3f})\n"
        return answer
    
    demo = gr.ChatInterface(
        fn=chat,
        title="📚 RAG智能问答系统",
        description="基于检索增强生成的知识问答助手"
    )
    demo.launch()

if __name__ == "__main__":
    main()