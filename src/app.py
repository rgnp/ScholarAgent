import streamlit as st
import tempfile
import os
import sys

# 确保能导入同目录下的模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools import parse_paper
from researcher import generate_research_report

# 页面配置
st.set_page_config(page_title="ScholarAgent", layout="wide", page_icon="🎓")

# --- 侧边栏：配置与上传 ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/student-male--v1.png", width=80)
    st.title("ScholarAgent")
    st.caption("你的全能科研助理：读论文 + 查趋势 + 定位生态")
    
    uploaded_file = st.file_uploader("上传一篇 PDF 论文", type=["pdf"])
    
    st.markdown("---")
    st.markdown("### 🛠️ 核心能力")
    st.markdown("- **LlamaParse**: 深度解析 PDF")
    st.markdown("- **Tavily**: 联网调研领域趋势")
    st.markdown("- **DeepSeek**: 综合推理与写作")

# --- 主界面 ---
st.title("📑 智能论文深度研报")

# 初始化 session state 用于存储报告
if "report" not in st.session_state:
    st.session_state.report = ""

if uploaded_file:
    # 显示文件名
    st.info(f"已加载文件: {uploaded_file.name}")

    # 大大的开始按钮
    if st.button("开始深度分析", type="primary", use_container_width=True):
        
        # 初始化进度条
        progress_bar = st.progress(0, text="准备开始...")
        
        # 定义一个局部更新函数，确保能访问到 progress_bar
        def current_status_updater(text, p):
            progress_bar.progress(p, text=text)
        
        try:
            # 1. 保存临时文件 (因为 LlamaParse 需要文件路径)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            # 2. 解析 PDF
            current_status_updater("正在进行 OCR 与 深度解析 (LlamaParse)...", 0.1)
            paper_content = parse_paper(tmp_path)
            
            # 3. 生成报告 (核心逻辑)
            # 传入我们的更新函数
            report = generate_research_report(paper_content, current_status_updater)
            
            # 存入 session state
            st.session_state.report = report
            
            # 清理临时文件
            os.remove(tmp_path)
            
        except Exception as e:
            st.error(f"发生错误: {str(e)}")
        
        # 尝试移除进度条
        try:
            progress_bar.empty()
        except:
            pass

# --- 展示结果 ---
if st.session_state.report:
    st.divider()
    st.success("分析完成！")
    
    # 左右分栏：左边是大纲导航（可选），右边是正文
    col1, col2 = st.columns([0.1, 0.9])
    
    with col2:
        # 渲染 Markdown 报告
        st.markdown(st.session_state.report)
        
        st.divider()
        # 下载按钮
        st.download_button(
            label="📥 下载研报 (.md)",
            data=st.session_state.report,
            file_name="research_report.md",
            mime="text/markdown"
        )
else:
    # 引导页
    if not uploaded_file:
        st.info("👈 请在左侧上传一篇你想要精读的论文 PDF")
    else:
        st.info("👆 点击“开始深度分析”，AI 将为你联网调研并生成报告")