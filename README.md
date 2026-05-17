
# RAG智能问答系统

基于检索增强生成（RAG）技术的智能问答系统，支持信息检索、推荐系统、知识图谱等领域知识问答。

## 项目简介

本项目实现了一个完整的RAG（Retrieval-Augmented Generation）智能问答系统。系统从PDF文档中提取知识，构建向量索引，通过混合检索（稠密检索+稀疏检索）召回相关文档片段，最后调用大语言模型生成带引用的答案。

### 主要功能

- 📚 **知识库构建**：从3个PDF文档中提取结构化知识，构建100条问答测试集
- 🔍 **混合检索**：融合FAISS稠密检索和BM25稀疏检索，提高召回准确性
- 🤖 **智能问答**：基于检索结果，调用大模型生成精准答案
- 📎 **引用溯源**：答案自动标注来源，支持追溯原始文档
- 💬 **Web界面**：基于Gradio的友好交互界面，支持多轮对话

## 技术架构

```
用户问题 → 混合检索 → 相关文档 → Prompt构建 → LLM生成 → 带引用答案
              ↓
        FAISS + BM25
```

### 技术栈

| 模块 | 技术 | 说明 |
|------|------|------|
| 嵌入模型 | BAAI/bge-small-zh-v1.5 | 国产中文嵌入模型 |
| 向量索引 | FAISS | 高效相似度检索 |
| 稀疏检索 | BM25 + jieba | 关键词匹配检索 |
| 大模型 | 阿里百炼Qwen | 国产大模型API |
| Web界面 | Gradio | 快速构建交互界面 |

## 快速开始

### 环境要求

- Python 3.8+
- 建议4GB以上内存

### 安装依赖

```bash
pip install -r requirements_preprocess.txt
```

如果安装慢，可使用清华镜像：

```bash
pip install -r requirements_preprocess.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 运行系统

```bash
python main.py
```

启动后，浏览器会自动打开 `http://127.0.0.1:7860`，即可使用。

### 测试示例

在界面中输入以下问题测试：

- "什么是信息检索？"
- "推荐系统有哪些常用的算法？"
- "知识图谱可以用来做什么？"

系统会返回基于文档的答案，并标注来源。

## 文件结构

```
AL_Project/
├── main.py                      # 系统主入口
├── requirements_preprocess.txt  # Python依赖列表
├── README.md                    # 项目说明文档
├── taskB_vectorize.py           # 向量化与索引构建（成员B）
├── taskC_hybrid_retriever.py    # 混合检索模块（成员C）
├── taskD_rag_generator.py       # RAG问答生成（成员D）
├── data/
│   ├── processed/               # 处理后的数据
│   │   ├── documents.jsonl      # 结构化文档库
│   │   ├── chunks.json          # 分块后的文本
│   │   ├── chunks_with_metadata.json  # 带元数据的chunks
│   │   ├── faiss_index.bin      # FAISS向量索引
│   │   ├── embeddings.npy       # 向量数组
│   │   ├── qa_pairs.json        # 100条问答测试集
│   │   └── README_data.md       # 数据说明文档
│   └── raw/                     # 原始PDF文档
│       ├── 人工智能之信息检索与推荐.pdf
│       ├── 人工智能之知识图谱.pdf
│       └── 人工智能十万个为什么：热AI冷知识.pdf
```

## 评估结果

基于100条问答测试集的评估结果：

| 指标 | 结果 |
|------|------|
| 检索平均得分 | 0.75 |
| 平均响应时间 | < 2秒 |
| 引用准确率 | 85% |

## 团队成员及分工

| 成员 | 负责模块 | 核心任务 |
|------|----------|----------|
| 成员A | 数据采集与知识库构建 | 3个PDF数据提取、100条QA测试集 |
| 成员B | 文本预处理与向量化 | 分块策略、BGE嵌入、FAISS索引 |
| 成员C | 混合检索模块 | FAISS+BM25融合检索 |
| 成员D | LLM集成与问答生成 | RAG Prompt设计、大模型调用 |
| 成员E | Web界面与评估 | Gradio界面、RAGAS评估 |
| 成员F | 系统集成与文档答辩 | 代码整合、文档撰写、PPT、视频 |

## 难点与解决方案

| 难点 | 解决方案 |
|------|----------|
| FAISS中文路径写入失败 | 使用临时英文路径中转 |
| 嵌入模型下载慢 | 使用ModelScope国内镜像 |
| API网络超时 | 增加超时设置，支持模拟模式 |

## 未来改进方向

- 接入GraphRAG，融合知识图谱提升复杂推理能力
- 部署到HuggingFace Spaces，提供在线演示
- 支持多模态检索（图文混合）

## 致谢

感谢阿里云百炼提供的免费大模型API额度，感谢BAAI开源的bge嵌入模型。

## 联系方式

项目地址：[https://github.com/l1355468-design/RAG-QA-System]


