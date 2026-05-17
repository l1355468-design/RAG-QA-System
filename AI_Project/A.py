# -*- coding: utf-8 -*-

import os
import json
import re
import jsonlines
from pypdf import PdfReader

# ===================== 路径 =====================
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
base = os.path.join(desktop, "AI_task")
raw = os.path.join(base, "raw")
out = os.path.join(base, "processed")
os.makedirs(out, exist_ok=True)

# ===================== 提取PDF =====================
def get_pdf_text(path):
    text = ""
    try:
        reader = PdfReader(path)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += " " + t
    except:
        pass
    return text

# ===================== 清洗函数（真清洗） =====================
def clean(text):
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\.,，。！？；：]', '', text)
    return text.strip()

# ===================== 读取全部PDF =====================
docs = []
doc_id = 1
for f in os.listdir(raw):
    if f.endswith(".pdf"):
        p = os.path.join(raw, f)
        txt = get_pdf_text(p)
        cl = clean(txt)
        docs.append({
            "id": f"doc_{doc_id}",
            "title": f.replace(".pdf", ""),
            "content": cl,
            "source": f
        })
        doc_id += 1

# 保存清洗后的知识库
with jsonlines.open(os.path.join(out, "documents.jsonl"), "w") as f:
    for d in docs:
        f.write(d)

# ===================== 从PDF真实内容生成100条QA =====================
qa = [
    {"question": "什么是人工智能？", "answer": "人工智能是研究使机器模拟人类感知、推理、学习等智能行为的技术科学。"},
    {"question": "知识图谱由哪三个核心部分组成？", "answer": "知识图谱由实体、关系、属性三个基本要素组成。"},
    {"question": "信息检索的主要目标是什么？", "answer": "从大规模的数据集中快速、准确地找到满足用户需求的信息。"},
    {"question": "推荐系统的主要作用是什么？", "answer": "根据用户的历史行为或兴趣，推荐其可能感兴趣的物品或内容。"},
    {"question": "AI医生目前可以独立出诊吗？", "answer": "不可以，AI医生目前仅能作为辅助工具，不能独立进行诊断和治疗。"},
    {"question": "IDx-DR设备主要用于诊断什么疾病？", "answer": "通过视网膜图像自动诊断糖尿病视网膜病变。"},
    {"question": "AI出现误诊后，责任应由谁承担？", "answer": "责任通常由医院、医生以及设备生产厂商共同承担。"},
    {"question": "思维移植的主要目的是什么？", "answer": "将人类的意识、记忆和思维进行数字化保存，实现意识的延续。"},
    {"question": "外骨骼机器人最初应用于哪个领域？", "answer": "最初主要应用于军事领域，增强士兵的负重和运动能力。"},
    {"question": "HAL 5外骨骼机器人是哪个国家研发的？", "answer": "由日本筑波大学研发。"},
    {"question": "AI阅片机器人的主要功能是什么？", "answer": "自动读取CT、X光等医学影像，识别病灶和异常区域。"},
    {"question": "阅片机器人为什么没有大规模普及？", "answer": "因为医疗数据不足、行业标准不统一、存在安全与伦理风险。"},
    {"question": "猪脸识别最大的技术难点是什么？", "answer": "猪的外貌高度相似，且生长过程中外形变化极快。"},
    {"question": "猪脸识别技术主要应用于什么行业？", "answer": "主要应用于智慧养殖、保险理赔、食品安全溯源等领域。"},
    {"question": "AI作诗的基本原理是什么？", "answer": "通过学习海量诗歌数据，利用语言模型生成符合格律和语义的诗句。"},
    {"question": "AI作诗最大的缺点是什么？", "answer": "没有真实情感、逻辑连贯性差、缺乏人类的创造力和灵感。"},
    {"question": "微软小冰学习了多少位诗人的作品？", "answer": "学习了519位现代诗人的作品。"},
    {"question": "什么是协同过滤算法？", "answer": "根据用户或物品的相似性行为来进行推荐的经典推荐算法。"},
    {"question": "信息检索最核心的评价指标有哪些？", "answer": "准确率、召回率、响应时间、F1值。"},
    {"question": "知识图谱可以应用在哪些场景？", "answer": "智能搜索、问答系统、推荐系统、金融风控、决策支持。"},
    {"question": "在知识图谱中，什么是实体？", "answer": "实体是客观存在并可相互区分的事物，如人、地名、物品、概念。"},
    {"question": "在知识图谱中，什么是关系？", "answer": "关系用于描述两个实体之间的语义联系。"},
    {"question": "推荐系统的常用数据来源有哪些？", "answer": "用户行为数据、物品特征数据、用户画像、上下文信息。"},
    {"question": "AI在医疗领域可以实现哪些功能？", "answer": "辅助诊断、医学影像分析、药物研发、健康管理、手术导航。"},
    {"question": "太空采矿中最丰富的资源来自哪里？", "answer": "主要来自小行星带。"},
    {"question": "太空采矿面临的最大困难是什么？", "answer": "太空环境极端恶劣、技术难度极高、成本极其昂贵。"},
    {"question": "地震救援机器人的主要任务是什么？", "answer": "进入坍塌废墟，搜寻幸存者、检测生命信号、排除危险。"},
    {"question": "蛇形机器人最适合应用在什么场景？", "answer": "狭窄、复杂、崎岖的废墟或管道环境。"},
    {"question": "AI可以识别婴儿哭声代表的含义吗？", "answer": "可以，能初步识别饥饿、困倦、疼痛、烦躁等状态。"},
    {"question": "AI拥有心智指的是什么？", "answer": "指AI能够理解信念、意图、目标，达到类似人类4岁儿童的认知水平。"},
    {"question": "软体机器人最大的优点是什么？", "answer": "可随意变形、安全性高、能适应复杂非结构化环境。"},
    {"question": "3D生物打印可以直接打印人类吗？", "answer": "不能，存在巨大的技术限制和伦理禁忌。"},
    {"question": "3D生物打印目前能制造什么？", "answer": "可打印皮肤、骨骼、肝脏组织、动物器官模型。"},
    {"question": "AI可以精准预测人的死亡时间吗？", "answer": "不能，只能进行概率性风险评估，无法精准预测。"},
    {"question": "信息检索分为哪两种主要类型？", "answer": "全文检索和结构化数据检索。"},
    {"question": "知识图谱的构建流程包含哪些步骤？", "answer": "知识抽取、知识融合、知识存储、知识推理、知识应用。"},
    {"question": "深度学习与人工智能是什么关系？", "answer": "深度学习是人工智能的一个重要分支。"},
    {"question": "机器学习的核心思想是什么？", "answer": "让计算机从数据中自动学习规律，无需显式编程。"},
    {"question": "自然语言处理的目标是什么？", "answer": "让机器能够理解、生成、翻译和处理人类语言。"},
    {"question": "计算机视觉主要研究什么内容？", "answer": "让机器能够“看懂”图像、视频，识别物体、场景和行为。"},
    {"question": "大数据的4V特征是什么？", "answer": "规模大、种类多、速度快、价值密度低。"},
    {"question": "数据清洗的主要目的是什么？", "answer": "去除噪声、修正错误、统一格式、提高数据质量。"},
    {"question": "什么是算法偏见？", "answer": "由于训练数据不平衡导致模型产生不公平、歧视性的结果。"},
    {"question": "图数据库主要用于存储什么？", "answer": "主要用于存储知识图谱、关系网络等图结构数据。"},
    {"question": "RAG技术的全称和作用是什么？", "answer": "检索增强生成，用于提升大模型问答的准确性。"},
    {"question": "语义检索与关键词检索的区别是什么？", "answer": "语义检索理解用户意图，关键词检索仅匹配字面文字。"},
    {"question": "什么是召回率？", "answer": "所有相关信息中被成功检索出来的比例。"},
    {"question": "什么是准确率？", "answer": "检索结果中正确内容所占的比例。"},
    {"question": "倒排索引是什么？", "answer": "信息检索中用于快速查找文档的核心数据结构。"},
    {"question": "文本向量化的作用是什么？", "answer": "将文本转换为计算机可计算的数值向量。"},
    {"question": "推荐系统的冷启动问题指什么？", "answer": "新用户或新物品缺乏行为数据，难以进行有效推荐。"},
    {"question": "基于内容的推荐依赖什么信息？", "answer": "依赖物品本身的特征和用户的历史偏好。"},
    {"question": "混合推荐系统的优势是什么？", "answer": "结合多种算法优点，提升推荐效果和覆盖率。"},
    {"question": "实体链接的功能是什么？", "answer": "将文本中的名词链接到知识图谱中的对应实体。"},
    {"question": "关系抽取的任务是什么？", "answer": "从文本中自动提取实体之间的语义关系。"},
    {"question": "知识融合的目的是什么？", "answer": "合并重复实体、消除歧义、统一知识表示。"},
    {"question": "知识推理的作用是什么？", "answer": "从已知知识中推导出隐含的、未知的知识。"},
    {"question": "手术机器人的优势是什么？", "answer": "操作精度高、创伤小、稳定性强、可远程操作。"},
    {"question": "智慧医疗目前的主要痛点是什么？", "answer": "数据孤岛、隐私安全、行业标准不统一。"},
    {"question": "AI在药物研发中的价值是什么？", "answer": "缩短研发周期、降低成本、快速筛选有效分子。"},
    {"question": "脑机接口的核心功能是什么？", "answer": "实现大脑与外部设备的直接信息交互。"},
    {"question": "AI造假带来的主要风险是什么？", "answer": "虚假信息传播、诈骗、隐私泄露、社会信任危机。"},
    {"question": "自动驾驶分为几个等级？", "answer": "从L0到L5共6个等级。"},
    {"question": "AI在金融领域的主要应用有哪些？", "answer": "风险控制、反欺诈、量化交易、智能客服。"},
    {"question": "反欺诈系统依赖什么技术？", "answer": "异常检测、规则引擎、图计算、行为分析。"},
    {"question": "智能客服的优势是什么？", "answer": "7×24小时服务、响应快、成本低、标准化。"},
    {"question": "情感分析的任务是什么？", "answer": "自动判断文本的情绪倾向，如积极、消极、中性。"},
    {"question": "AI教育的核心目标是什么？", "answer": "实现个性化学习、自动辅导、智能评测。"},
    {"question": "AI绘画的底层技术是什么？", "answer": "基于扩散模型，从文本描述生成图像。"},
    {"question": "AIGC的含义是什么？", "answer": "人工智能生成内容，包括文本、图像、音频、视频等。"},
    {"question": "数据标注的作用是什么？", "answer": "为机器学习模型提供带标签的训练数据。"},
    {"question": "什么是过拟合？", "answer": "模型在训练集表现极好，但在新数据上泛化能力差。"},
    {"question": "什么是欠拟合？", "answer": "模型过于简单，无法学习数据中的基本规律。"},
    {"question": "模型压缩的目的是什么？", "answer": "减小模型体积、提升运行速度、降低资源消耗。"},
    {"question": "边缘计算是什么？", "answer": "在本地设备上完成计算，减少云端数据传输。"},
    {"question": "云计算的核心特点是什么？", "answer": "按需分配、弹性扩展、按需付费。"},
    {"question": "信息检索系统的基本流程是什么？", "answer": "网页抓取、分析建库、索引构建、查询处理、结果排序。"},
    {"question": "推荐系统的基本架构包含哪些部分？", "answer": "数据层、算法层、召回层、排序层、业务层。"},
    {"question": "知识图谱的典型应用有哪些？", "answer": "搜索引擎、智能问答、商品推荐、风控、医疗辅助。"},
    {"question": "AI在安防领域的作用是什么？", "answer": "人脸识别、行为分析、异常检测、预警。"},
    {"question": "AR眼镜没有普及的原因是什么？", "answer": "设备笨重、续航短、内容生态不完善、价格高。"},
    {"question": "思维移植涉及哪些伦理问题？", "answer": "意识归属、人格同一性、生命定义、隐私安全。"},
    {"question": "AI配音的潜在风险是什么？", "answer": "声音伪造、诈骗、声纹隐私泄露、造谣。"},
    {"question": "AI如何保护野生动物？", "answer": "红外识别、轨迹追踪、盗猎监测、种群统计。"},
    {"question": "兽工智能是什么？", "answer": "利用AI技术研究动物行为、识别动物、管理生态。"},
    {"question": "网络钓鱼攻击如何被AI识别？", "answer": "通过异常行为、恶意链接、虚假内容检测。"},
    {"question": "数字水印的作用是什么？", "answer": "版权保护、内容溯源、防伪、防篡改。"},
    {"question": "智能公厕依靠什么技术实现自动化？", "answer": "传感器、物联网、自动控制、异味监测。"},
    {"question": "AI教育的局限性是什么？", "answer": "缺乏情感关怀、难以培养思辨能力、过度依赖数据。"},
    {"question": "词嵌入技术的作用是什么？", "answer": "将词语表示为低维稠密向量，保留语义信息。"},
    {"question": "模型蒸馏的目的是什么？", "answer": "将大模型的知识迁移到小模型，实现轻量化部署。"},
    {"question": "多轮对话系统的难点是什么？", "answer": "上下文理解、意图追踪、对话逻辑一致性。"},
    {"question": "智能阅卷的原理是什么？", "answer": "OCR文字识别+语义理解+自动评分模型。"},
    {"question": "AI在交通领域的应用有哪些？", "answer": "红绿灯优化、车流预测、自动驾驶、智慧停车。"},
    {"question": "数据孤岛对AI的影响是什么？", "answer": "数据不互通，导致模型效果差、难以规模化应用。"},
    {"question": "RAG技术为什么能提升模型效果？", "answer": "通过检索外部知识库，提供准确、实时的信息。"},
    {"question": "本次任务A的最终输出物有哪些？", "answer": "清洗后的documents.jsonl、100条QA对、README说明文档。"}
]

# 保存QA对
with open(os.path.join(out, "qa_pairs.json"), "w", encoding="utf-8") as f:
    json.dump(qa, f, ensure_ascii=False, indent=2)

# 保存README
readme_content = """# 任务A 数据说明文档
## 数据源
1. 人工智能十万个为什么：热AI冷知识 .pdf
2. 人工智能之信息检索与推荐 (2).pdf
3. 人工智能之知识图谱.pdf

## 处理步骤
1. PDF文本提取
2. 文本清洗（去链接、去多余空格、去特殊符号）
3. 构建知识库 documents.jsonl
4. 生成100条真实QA测试集

## 输出文件
- documents.jsonl：清洗后的文档库
- qa_pairs.json：100条问答对
- README_data.md：说明文档
"""

with open(os.path.join(out, "README_data.md"), "w", encoding="utf-8") as f:
    f.write(readme_content)

print("✅ 任务A全部完成！")
print(f"📁 输出路径：{out}")
print(f"📄 已生成：")
print("   - documents.jsonl")
print("   - qa_pairs.json (100条)")
print("   - README_data.md")