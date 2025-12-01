import os
import json
from openai import OpenAI
from tools import web_search

# 初始化 DeepSeek 客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL")
)

def generate_research_report(paper_content, status_callback):
    """
    输入：论文全文
    输出：深度分析报告 (Markdown)
    参数：status_callback 用于更新前端进度条
    """
    
    # --- Step 1: 初步阅读与提取元数据 ---
    status_callback("正在阅读论文，提取核心脉络与前人工作...", 0.2)
    
    # 让 AI 在读论文时，特意留意一下它引用了谁（Baselines）
    extract_prompt = f"""
    请阅读以下论文内容，提取以下关键信息，返回 JSON 格式：
    1. 论文标题 (title)
    2. 具体研究领域 (domain)
    3. 核心方法关键词 (keywords) - 3个
    4. 论文中明确提到的核心基线模型或前人基础工作 (baselines) - 提取2-3个关键论文名或方法名
    
    [论文内容摘要]:
    {paper_content[:15000]} 
    """
    
    try:
        res = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": extract_prompt}],
            response_format={"type": "json_object"}
        )
        meta_data = json.loads(res.choices[0].message.content)
        title = meta_data.get('title', 'Target Paper')
        domain = meta_data.get('domain', 'AI Research')
        baselines = meta_data.get('baselines', [])
        # 处理 baselines 可能是列表或字符串的情况
        baselines_str = ", ".join(baselines) if isinstance(baselines, list) else str(baselines)
    except Exception as e:
        print(f"Meta extraction failed: {e}")
        domain = "Computer Science"
        title = "Uploaded Paper"
        baselines_str = "Previous Standard Works"
    
    print(f"[Analysis] Domain: {domain} | Title: {title} | Based on: {baselines_str}")

    # --- Step 2: 联网调研 (外部视角 + 引用脉络) ---
    status_callback(f"正在全网搜索 '{title}' 的学术族谱与后续影响...", 0.4)
    
    # 构造针对性的搜索查询
    # 1. 领域宏观趋势
    search_q1 = f"{domain} research trends 2024 2025 state of the art"
    # 2. 论文本身的影响力/评价/代码
    search_q2 = f"{title} paper reviews impact github code implementation"
    
    # 🔥 核心升级：专门搜它的“父亲”和“孩子” 🔥
    # 3. 【学术上游】它基于谁？(验证提取的基线是否准确，找核心痛点)
    search_q3 = f"What papers inspired {title}? foundations based on {baselines_str}"
    # 4. 【学术下游】谁引用了它？(后续发展)
    search_q4 = f"papers citing {title} improvements extensions 2024 2025"
    
    # 执行搜索 (串行执行，确保稳定性)
    web_info_trends = web_search(search_q1)
    web_info_impact = web_search(search_q2)
    web_info_lineage = web_search(search_q3 + " " + search_q4)
    
    # --- Step 3: 深度综合分析 (生成报告) ---
    status_callback("正在梳理学术族谱，进行费曼式拆解...", 0.8)
    
    final_prompt = f"""
    你是一位对学术脉络有深刻洞察、且善于教学的计算机博导。
    请根据【论文原文】和【外部情报】，为你的研究生写一份“全方位”的精读报告。
    
    目标：既要讲清技术原理（费曼技巧），又要理清它在学术历史中的承前启后关系。
    
    【论文元数据】
    标题: {title}
    领域: {domain}
    原文提及基线: {baselines_str}
    
    【外部情报 (趋势/评价/引用关系)】
    {web_info_trends}
    {web_info_impact}
    {web_info_lineage}
    
    【论文原文片段】
    {paper_content[:20000]}
    
    ---
    请严格按照以下 Markdown 结构输出报告（使用中文）：
    
    # 📑 {title} - 深度精读报告
    
    ## 1. 全局视野：这篇论文在解决什么？(The "Why")
    * **背景与痛点**：用大白话解释，这篇论文出现之前，这个领域大家都在头疼什么问题？
    * **核心洞察**：作者发现了什么别人没发现的盲点？
    
    ## 2. 核心魔法：它是怎么做到的？(The "How")
    * **通俗类比 (关键)**：请打一个生活中的比方来解释它的核心算法/架构。（例如：把Transformer比作传声筒...）
    * **技术路线图**：简单梳理它的步骤（Step 1, Step 2...）。
    
    ## 3. 学术谱系：承前启后 (The Lineage)
    *(这是重点，请详细分析)*
    * **👉 它的父亲 (Foundations)**：这篇论文的核心思想是基于哪些经典工作（如 {baselines_str}）发展而来的？它是对前人的微调还是颠覆？(请列出具体论文名)
    * **👉 它的孩子 (Future Works)**：(结合外部搜索结果) 在它发表之后，有哪些新的论文引用了它？或者在它的基础上做了哪些改进？(如果搜索不到具体论文，请根据技术趋势预测未来的改进方向)。
    
    ## 4. 学术生态位与评价
    * **横向对比**：相比 SOTA 的优势与劣势。
    * **影响力检查**：开源情况与社区反馈。
    
    ## 5. 费曼转述指南：如何给别人讲懂？
    * **一句话电梯演讲**：“如果只能用一句话介绍这篇论文，你应该说：...”
    * **30秒逻辑链**：“起因是... 既然旧方法有...的问题，于是作者提出了... 结果发现...”
    * **可能的质疑点**：别人听完可能会问什么刁钻的问题？请预判并给出回答思路。
    
    ## 6. 导师点评
    * **推荐指数**：(1-5星)
    * **一句话总结**：是否值得精读？
    """
    
    completion = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": final_prompt}],
        temperature=0.5
    )
    
    status_callback("分析完成！", 1.0)
    return completion.choices[0].message.content