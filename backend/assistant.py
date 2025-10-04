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
            description="本地新闻知识库工具：包含完整的新闻数据、历史事件、实时信息等。这是主要的信息来源，应该优先使用。适用于所有类型的查询，包括最新新闻、历史事件、人物信息等。如果返回的结果与问题不相关、为空或包含'Placeholder text'，则必须使用OnlineSearch工具。"
        ),
        Tool(
            name="OnlineSearch",
            func=online_search_tool.invoke,
            description="在线搜索工具：当本地知识库无法提供相关信息时必须使用此工具。使用条件：1)本地知识库返回空结果 2)返回内容与问题不相关 3)返回内容包含'Placeholder text' 4)返回内容无法回答用户问题。"
        )
    ]
    
    # 设置agent参数，强调本地知识库优先策略
    agent_kwargs = {
        "system_message": """
        你是一个智能助手，专门为新闻知识库系统服务。请严格按以下步骤工作：

        1. **默认策略**：始终优先使用本地新闻知识库工具
           - 本地知识库包含完整的新闻数据、历史事件、实时信息等
           - 对于所有查询，首先尝试从本地知识库获取信息

        2. **搜索策略**：
           - 分析用户问题，提取关键搜索词
           - 使用提取的关键词查询本地知识库
           - 如果本地知识库返回的结果与问题不相关、为空或内容为"Placeholder text"，则必须使用在线搜索

        3. **工具使用顺序**：
           - 第一步：使用KnowledgeBase工具查询本地知识库
           - 第二步：评估本地知识库结果是否相关和有用
           - 第三步：如果本地结果不相关或无用，立即使用OnlineSearch工具
           - 第四步：基于搜索结果提供准确、有依据的回答

        4. **结果评估标准**：
           - 如果本地知识库返回的内容与用户问题不匹配
           - 如果返回的内容为空或包含"Placeholder text"
           - 如果返回的内容无法回答用户的问题
           - 满足以上任一条件，都必须使用在线搜索

        5. **回答质量**：
           - 优先基于本地知识库的信息回答问题
           - 如果本地知识库信息不足，必须使用在线搜索补充
           - 明确标注信息来源（本地知识库 vs 在线搜索）
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
    # 使用LLM提取关键词，优化本地知识库搜索
    llm = Ollama(model="qwen2.5:3b", temperature=0)
    
    # 提取搜索关键词
    keyword_prompt = f"""
    分析以下用户问题，提取最适合在新闻知识库中搜索的关键词：
    
    用户问题：{query}
    
    请提取2-4个关键词，用于在本地新闻知识库中搜索相关信息。
    关键词应该简洁、准确，能够匹配新闻内容。
    
    请回答格式：
    搜索关键词：[关键词1, 关键词2, 关键词3]
    """
    
    keyword_analysis = llm.invoke(keyword_prompt)
    print(f"关键词分析：{keyword_analysis}")
    
    # 创建工具
    knowledge_base_tool = create_knowledge_base_tool()
    online_search_tool = create_online_search_tool()
    
    raw_sources = []
    origin = "none"
    
    # 第一步：始终优先查询本地知识库
    print("正在查询本地新闻知识库...")
    raw_sources = knowledge_base_tool.invoke({"action": "retrieve", "query": query, "k": 5, "rerank": True})
    origin = "knowledge_base"
    
    # 检查知识库结果是否有效和相关
    def is_knowledge_base_result_invalid(sources, user_query):
        if not isinstance(sources, list) or len(sources) == 0:
            return True
        
        # 检查是否所有结果都是占位符文本
        all_placeholder = True
        for source in sources:
            content = str(source.get("content", "")).strip()
            if content and content != "Placeholder text":
                all_placeholder = False
                break
        
        if all_placeholder:
            return True
        
        # 使用LLM判断结果是否与用户问题相关
        relevance_prompt = f"""
        判断以下搜索结果是否与用户问题相关：
        
        用户问题：{user_query}
        
        搜索结果：
        {str(sources[:2])}  # 只检查前2个结果
        
        请回答：相关/不相关
        如果搜索结果与用户问题主题不匹配，回答"不相关"
        """
        
        try:
            relevance_check = llm.invoke(relevance_prompt)
            if "不相关" in relevance_check:
                return True
        except Exception:
            pass  # 如果判断失败，继续使用原始结果
        
        return False
    
    is_knowledge_base_empty = is_knowledge_base_result_invalid(raw_sources, query)
    
    # 第二步：如果本地知识库没有有效结果，才使用在线搜索
    if is_knowledge_base_empty:
        print("本地知识库无相关数据，正在使用在线搜索...")
        origin = "online_search"
        raw_sources = online_search_tool.invoke(query)
        if not isinstance(raw_sources, list):
            raw_sources = []
    else:
        print("本地知识库找到相关数据，使用本地结果")

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
    
    # 测试查询 - 所有问题都应该优先查询本地新闻知识库
    test_queries = [
        "国民党主席选举",  # 应该能在本地知识库找到
        "最近有什么灾害吗",  # 本地可能没有，应该fallback到在线搜索
        "今天股市行情如何",  # 本地可能没有，应该fallback到在线搜索
        "人工智能最新发展",  # 本地可能没有，应该fallback到在线搜索
    ]
    
    print("=== 智能助手测试 ===")
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"问题: {query}")
        print("-" * 50)
        try:
            result = assistant.invoke(query)
            print(f"回答: {result}")
        except Exception as e:
            print(f"查询出错: {str(e)}")
    
    print(f"\n{'='*50}")
    print("=== 带来源的查询测试 ===")
    for query in test_queries[:2]:  # 只测试前两个问题
        print(f"\n{'='*50}")
        print(f"问题: {query}")
        print("-" * 50)
        try:
            result = query_with_sources(query)
            print(f"回答: {result['answer']}")
            print(f"来源: {result['origin']}")
        except Exception as e:
            print(f"查询出错: {str(e)}")