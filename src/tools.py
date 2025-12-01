import os
from dotenv import load_dotenv
from tavily import TavilyClient
from llama_parse import LlamaParse
import nest_asyncio

load_dotenv()
# 解决可能的异步事件循环问题
try:
    nest_asyncio.apply()
except:
    pass

def web_search(query):
    """
    【工具 1】联网搜索
    用于查找论文的影响力、领域热度、同类竞品等外部信息。
    """
    print(f"[Tool] Searching web for: {query}...")
    try:
        tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        # 使用 advanced 深度搜索
        response = tavily.search(query=query, search_depth="advanced", max_results=5)
        
        context = []
        
        # 🔥 核心修复：必须使用 response['results'] 而不是 response.results
        # Tavily 返回的是字典 (dict)，不是对象
        if 'results' in response:
            results = response['results']
        else:
            return "No results found."

        for result in results:
            # 使用 .get() 防止缺少字段报错
            title = result.get('title', 'No Title')
            url = result.get('url', '#')
            content = result.get('content', 'No Content')
            context.append(f"Source: {title}\nURL: {url}\nContent: {content}\n")
        
        return "\n---\n".join(context)
        
    except Exception as e:
        print(f"[Error] Web search failed: {e}")
        return f"Search error: {str(e)}"

def parse_paper(file_path):
    """
    【工具 2】论文解析 (基于 Week 1)
    用于读取 PDF 的全文内容。
    """
    print(f"[Tool] Parsing PDF: {file_path}...")
    try:
        parser = LlamaParse(
            api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
            result_type="markdown",
            verbose=True,
            language="en"
        )
        documents = parser.load_data(file_path)
        
        if not documents:
            return "Error: No text extracted from PDF."
            
        # 全文拼接
        return "\n\n".join([doc.text for doc in documents])
        
    except Exception as e:
        print(f"[Error] Parsing failed: {e}")
        return f"Parsing error: {str(e)}"