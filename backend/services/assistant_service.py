"""
Assistant service for AI query processing.
"""
from typing import Dict, Any, List, Optional
from sqlmodel import Session
from langchain_community.llms import Ollama
from langchain.agents import initialize_agent, AgentType
from langchain.agents import Tool
from services.knowledge_base.vector_store_service import vector_store_service
from services.search.online_search_service import online_search_service
from schemas.assistant_schema import (
    AssistantQueryRequest, AssistantQueryResponse, SearchResult,
    AssistantHealthResponse, KnowledgeBaseStoreRequest, KnowledgeBaseResponse
)
from utils.logging_config import app_logger
from config.settings import settings


class AssistantService:
    """Service for AI assistant operations."""
    
    def __init__(self, session: Session):
        self.session = session
        self.assistant = None
        self._initialize_assistant()
    
    def _initialize_assistant(self):
        """Initialize the AI assistant."""
        try:
            # Initialize LLM
            model_name = "qwen2.5:3b"
            llm = Ollama(model=model_name, temperature=0)
            
            # Create tools
            knowledge_base_tool = self._create_knowledge_base_tool()
            online_search_tool = online_search_service.create_search_tool()
            
            # Define tools list
            tools = [
                Tool(
                    name="KnowledgeBase",
                    func=lambda query: knowledge_base_tool.invoke({
                        "action": "retrieve", 
                        "query": query, 
                        "k": 3, 
                        "rerank": True
                    }),
                    description="本地新闻知识库工具：包含完整的新闻数据、历史事件、实时信息等。这是主要的信息来源，应该优先使用。适用于所有类型的查询，包括最新新闻、历史事件、人物信息等。如果返回的结果与问题不相关、为空或包含'Placeholder text'，则必须使用OnlineSearch工具。"
                ),
                Tool(
                    name="OnlineSearch",
                    func=online_search_tool.invoke,
                    description="在线搜索工具：当本地知识库无法提供相关信息时必须使用此工具。使用条件：1)本地知识库返回空结果 2)返回内容与问题不相关 3)返回内容包含'Placeholder text' 4)返回内容无法回答用户问题。"
                )
            ]
            
            # Set agent parameters
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
            
            # Initialize agent
            self.assistant = initialize_agent(
                tools=tools,
                llm=llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5,
                max_execution_time=180,
                agent_kwargs=agent_kwargs
            )
            
            app_logger.info("Assistant initialized successfully")
        except Exception as e:
            app_logger.error(f"Failed to initialize assistant: {str(e)}")
            raise
    
    def _create_knowledge_base_tool(self):
        """Create knowledge base tool."""
        from langchain_core.tools import StructuredTool
        
        def knowledge_base_func(action: str, documents: List[dict] = None, 
                              query: str = None, k: int = 3, rerank: bool = True):
            """Knowledge base tool function."""
            if action == "store":
                if documents:
                    result = vector_store_service.add_documents(documents)
                    return result
                return "No documents provided"
            elif action == "retrieve":
                if query:
                    results = vector_store_service.search(query, k, rerank)
                    return results
                return []
            else:
                return f"Unsupported action: {action}"
        
        return StructuredTool.from_function(
            func=knowledge_base_func,
            name="KnowledgeBase",
            description="用于处理和检索向量数据库中的知识，支持存储文档(store)和检索信息(retrieve)两种操作"
        )
    
    def process_query(self, request: AssistantQueryRequest) -> AssistantQueryResponse:
        """Process a user query."""
        try:
            app_logger.info(f"Processing query: {request.query}")
            
            # Use the new query function with sources
            result = self._query_with_sources(request.query)
            
            # Extract components
            final_answer = result.get("answer", "")
            raw_sources = result.get("raw_sources", [])
            origin = result.get("origin", "knowledge_base")
            
            # Format sources
            sources = self._format_sources(raw_sources)
            
            return AssistantQueryResponse(
                query=request.query,
                response=final_answer,
                answer=final_answer,
                sources=sources,
                raw_answer=raw_sources,
                origin=origin,
                status="success"
            )
        except Exception as e:
            app_logger.error(f"Error processing query: {str(e)}")
            return AssistantQueryResponse(
                query=request.query,
                response=f"Sorry, an error occurred: {str(e)}",
                answer=f"Sorry, an error occurred: {str(e)}",
                sources=[],
                raw_answer=None,
                origin="error",
                status="error"
            )
    
    def _query_with_sources(self, query: str) -> Dict[str, Any]:
        """Query with source tracking."""
        try:
            # Initialize LLM for keyword extraction
            llm = Ollama(model="qwen2.5:3b", temperature=0)
            
            # Extract keywords
            keyword_prompt = f"""
            分析以下用户问题，提取最适合在新闻知识库中搜索的关键词：
            
            用户问题：{query}
            
            请提取2-4个关键词，用于在本地新闻知识库中搜索相关信息。
            关键词应该简洁、准确，能够匹配新闻内容。
            
            请回答格式：
            搜索关键词：[关键词1, 关键词2, 关键词3]
            """
            
            keyword_analysis = llm.invoke(keyword_prompt)
            app_logger.info(f"Keyword analysis: {keyword_analysis}")
            
            # Query knowledge base first
            app_logger.info("Querying knowledge base...")
            raw_sources = vector_store_service.search(query, k=5, rerank=True)
            origin = "knowledge_base"
            
            # Check if knowledge base results are valid
            if self._is_knowledge_base_result_invalid(raw_sources, query):
                app_logger.info("Knowledge base results invalid, using online search...")
                origin = "online_search"
                raw_sources = online_search_service.search(query, max_results=3)
                if not isinstance(raw_sources, list):
                    raw_sources = []
            else:
                app_logger.info("Using knowledge base results")
            
            # Filter relevant sources
            relevant_sources = self._filter_relevant_sources(query, raw_sources)
            sources_for_prompt = relevant_sources if relevant_sources else raw_sources
            
            # Generate answer
            answer = self._generate_answer(query, sources_for_prompt, llm)
            
            return {
                "answer": answer,
                "raw_sources": raw_sources,
                "origin": origin
            }
        except Exception as e:
            app_logger.error(f"Error in query with sources: {str(e)}")
            raise
    
    def _is_knowledge_base_result_invalid(self, sources: List[dict], query: str) -> bool:
        """Check if knowledge base results are invalid."""
        if not isinstance(sources, list) or len(sources) == 0:
            return True
        
        # Check for placeholder text
        all_placeholder = True
        for source in sources:
            content = str(source.get("content", "")).strip()
            if content and content != "Placeholder text":
                all_placeholder = False
                break
        
        if all_placeholder:
            return True
        
        # Use LLM to check relevance
        try:
            llm = Ollama(model="qwen2.5:3b", temperature=0)
            relevance_prompt = f"""
            判断以下搜索结果是否与用户问题相关：
            
            用户问题：{query}
            
            搜索结果：
            {str(sources[:2])}
            
            请回答：相关/不相关
            """
            
            relevance_check = llm.invoke(relevance_prompt)
            return "不相关" in relevance_check
        except Exception:
            return False
    
    def _filter_relevant_sources(self, query: str, sources: List[dict]) -> List[dict]:
        """Filter sources for relevance."""
        try:
            query_terms = [term.strip().lower() for term in query.split() if term.strip()]
            if not query_terms:
                query_terms = [query.lower()]
        except Exception:
            query_terms = [str(query).lower()]
        
        filtered = []
        for source in sources or []:
            try:
                title = source.get("metadata", {}).get("title", "") if isinstance(source.get("metadata", {}), dict) else source.get("title", "")
                content = source.get("content", "")
                text = (title or "") + "\n" + (content or "")
                text_lower = text.lower()
                
                if any(term and term in text_lower for term in query_terms):
                    filtered.append(source)
            except Exception:
                continue
        
        return filtered
    
    def _generate_answer(self, query: str, sources: List[dict], llm) -> str:
        """Generate answer based on sources."""
        def format_sources(sources):
            lines = []
            for i, source in enumerate(sources[:3], 1):
                try:
                    title = source.get("metadata", {}).get("title", "") if isinstance(source.get("metadata", {}), dict) else source.get("title", "")
                    content = source.get("content", "")
                    url = source.get("url", "")
                    lines.append(f"[来源{i}] 标题: {title}\n内容: {content}\n链接: {url}")
                except Exception:
                    lines.append(str(source))
            return "\n\n".join(lines) if lines else "(无)"
        
        sources_block = format_sources(sources)
        
        prompt = (
            "你是一名智能助手。只依据给定的资料作答，不要编造。\n"
            "若资料中存在与问题无关的内容，请忽略无关内容。\n"
            "如果至少有一条相关资料，请给出与问题主题最相关的要点总结；\n"
            "仅当完全没有相关资料时回复：'暂无资料'。\n"
            "请用简洁中文回答。\n\n"
            f"用户问题：{query}\n\n"
            f"资料如下：\n{sources_block}\n\n"
            "基于以上资料，给出直接答案："
        )
        
        return llm.invoke(prompt)
    
    def _format_sources(self, raw_sources: List[dict]) -> List[SearchResult]:
        """Format sources for response."""
        sources = []
        if isinstance(raw_sources, list):
            for i, source in enumerate(raw_sources):
                if isinstance(source, dict):
                    sources.append(SearchResult(
                        id=str(i + 1),
                        title=source.get("metadata", {}).get("title", f"文档片段 {i + 1}"),
                        content=source.get("content", ""),
                        url="",
                        score=1.0 - (i * 0.1),
                        type="document",
                        source=source.get("metadata", {}).get("source", "知识库"),
                        relevance=1.0 - (i * 0.1),
                        timestamp=source.get("metadata", {}).get("pub_date", "")
                    ))
        return sources
    
    def health_check(self) -> AssistantHealthResponse:
        """Check assistant health."""
        try:
            if self.assistant is None:
                return AssistantHealthResponse(
                    status="unhealthy",
                    error="Assistant not initialized"
                )
            
            return AssistantHealthResponse(
                status="healthy",
                message="Assistant is ready to process queries"
            )
        except Exception as e:
            return AssistantHealthResponse(
                status="unhealthy",
                error=str(e)
            )
    
    def store_documents_in_knowledge_base(self, documents: List[Dict[str, Any]]) -> KnowledgeBaseResponse:
        """Store documents in knowledge base."""
        try:
            result = vector_store_service.add_documents(documents)
            return KnowledgeBaseResponse(
                result=result,
                success=True,
                message="Documents stored successfully"
            )
        except Exception as e:
            app_logger.error(f"Error storing documents in knowledge base: {str(e)}")
            return KnowledgeBaseResponse(
                result=None,
                success=False,
                message=f"Error storing documents: {str(e)}"
            )
