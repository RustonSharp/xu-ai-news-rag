from tools import create_knowledge_base_tool, create_online_search_tool
from langchain_community.llms import Ollama
from langchain.agents import initialize_agent, AgentType
from langchain.agents import Tool

def create_assistant():
    """创建一个智能助手，集成知识库和在线搜索功能"""
    # 使用本地的Ollama模型
    model_name = "qwen2.5:3b"
    llm = Ollama(model=model_name, temperature=0)
    
    # 创建知识库工具
    knowledge_base_tool = create_knowledge_base_tool()
    
    # 创建在线搜索工具
    online_search_tool = create_online_search_tool()
    
    # 定义工具列表
    tools = [
        Tool(
            name="KnowledgeBase",
            func=lambda query: knowledge_base_tool.invoke({"action": "retrieve", "query": query, "k": 3, "rerank": True}),
            description="首选工具：包含完整文学作品和专业文档的本地知识库。当查询涉及特定文学作品、历史文档或已存储的详细信息时，此工具能提供最准确、最完整且最相关的答案。对于所有查询，首先使用此工具。"
        ),
        Tool(
            name="OnlineSearch",
            func=online_search_tool.invoke,
            description="备选工具：用于搜索最新的网络信息。仅当你需要最新的、实时的信息或者确定知识库中没有相关内容时才使用此工具。"
        )
    ]
    
    # 设置agent参数，引导智能体优先使用知识库
    agent_kwargs = {
        "system_message": """
        你是一个智能助手，你必须首先使用知识库工具来回答问题。只有在知识库工具明确表示无法提供相关信息时，才使用在线搜索工具。
        知识库工具包含专业的文档和历史资料，能提供准确和完整的答案。
        使用工具的步骤：
        1. 首先调用知识库工具，查询相关信息
        2. 如果知识库工具返回了相关且有用的信息，则基于这些信息生成回答
        3. 只有当知识库工具返回的结果明确表示没有相关信息时，才使用在线搜索工具
        """
    }
    
    # 初始化智能助手代理
    assistant = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,
        max_execution_time=180,  # 3分钟超时
        agent_kwargs=agent_kwargs
    )
    
    return assistant

def query_with_sources(query):
    """查询并基于检索到的来源生成有依据的回答"""
    # 先检索来源
    knowledge_base_tool = create_knowledge_base_tool()
    raw_sources = knowledge_base_tool.invoke({"action": "retrieve", "query": query, "k": 5, "rerank": True})

    origin = "knowledge_base"
    if not isinstance(raw_sources, list) or len(raw_sources) == 0 or str(raw_sources[0].get("content", "")).strip() == "Placeholder text":
        origin = "online_search"
        online_search_tool = create_online_search_tool()
        raw_sources = online_search_tool.invoke(query)
        if not isinstance(raw_sources, list):
            raw_sources = []

    # 用检索到的来源来约束生成，避免模型跑题
    # 简单相关性过滤：仅保留标题/内容包含查询关键词的来源
    def filter_relevant_sources(q, sources):
        try:
            q_terms = [t.strip().lower() for t in q.split() if t.strip()]
            if not q_terms:
                q_terms = [q.lower()]
        except Exception:
            q_terms = [str(q).lower()]
        filtered = []
        for s in sources or []:
            try:
                title = s.get("metadata", {}).get("title", "") if isinstance(s.get("metadata", {}), dict) else s.get("title", "")
                content = s.get("content", "")
                hay = (title or "") + "\n" + (content or "")
                hay_lower = hay.lower()
                if any(term and term in hay_lower for term in q_terms):
                    filtered.append(s)
            except Exception:
                continue
        return filtered

    relevant_sources = filter_relevant_sources(query, raw_sources)
    # 若过滤后为空，则仍使用原始sources，但在提示中要求忽略无关内容
    sources_for_prompt = relevant_sources if len(relevant_sources) > 0 else (raw_sources if isinstance(raw_sources, list) else [])

    def format_sources(sources):
        lines = []
        for i, s in enumerate(sources[:3], 1):
            try:
                title = s.get("metadata", {}).get("title", "") if isinstance(s.get("metadata", {}), dict) else s.get("title", "")
                content = s.get("content", "")
                url = s.get("url", "")
                lines.append(f"[来源{i}] 标题: {title}\n内容: {content}\n链接: {url}")
            except Exception:
                lines.append(str(s))
        return "\n\n".join(lines) if lines else "(无)"

    sources_block = format_sources(sources_for_prompt)

    # 直接使用同一模型进行有依据的回答
    llm = Ollama(model="qwen2.5:3b", temperature=0)
    prompt = (
        "你是一名智能助手。只依据给定的资料作答，不要编造。\n"
        "若资料中存在与问题无关的内容，请忽略无关内容。\n"
        "如果至少有一条相关资料，请给出与问题主题最相关的要点总结；\n"
        "仅当完全没有相关资料时回复：‘暂无资料’。\n"
        "请用简洁中文回答。\n\n"
        f"用户问题：{query}\n\n"
        f"资料如下：\n{sources_block}\n\n"
        "基于以上资料，给出直接答案："
    )
    final_answer = llm.invoke(prompt)

    return {
        "answer": final_answer,
        "raw_sources": raw_sources,
        "origin": origin
    }

if __name__ == "__main__":
    # 创建并测试助手
    assistant = create_assistant()
    
    # 测试查询
    test_queries = [
        "最近有什么灾害吗",
    ]
    
    for query in test_queries:
        print(f"\n问题: {query}")
        try:
            result = assistant.invoke(query)
            print(f"回答: {result}")
        except Exception as e:
            print(f"查询出错: {str(e)}")