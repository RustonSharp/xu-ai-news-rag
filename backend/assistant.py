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
        max_execution_time=60,
        agent_kwargs=agent_kwargs
    )
    
    return assistant

if __name__ == "__main__":
    # 创建并测试助手
    assistant = create_assistant()
    
    # 测试查询
    test_queries = [
        "《倒悬的第七次日落》讲了什么",
    ]
    
    for query in test_queries:
        print(f"\n问题: {query}")
        try:
            result = assistant.invoke(query)
            print(f"回答: {result}")
        except Exception as e:
            print(f"查询出错: {str(e)}")