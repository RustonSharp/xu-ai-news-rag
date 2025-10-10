
import warnings
# 抑制huggingface_hub的resume_download弃用警告
warnings.filterwarnings("ignore", category=FutureWarning, module="huggingface_hub")

# 尝试加载dotenv以支持从.env文件中读取环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("提示：未安装python-dotenv库，环境变量将从系统中读取。")
    print("如果需要从.env文件中加载环境变量，请运行：pip install python-dotenv")

from langchain_core.tools import StructuredTool
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import CrossEncoder
import os
import sys
import getpass  
import requests
import json
from langchain_core.tools import Tool
from utils.logging_config import app_logger 
from models.document import Document
import numpy as np
import re
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
from collections import Counter


# 在线搜索工具
def create_online_search_tool():
    """创建一个可以进行在线搜索的工具"""
    # 尝试获取TAVILY API密钥
    tavily_api_key = os.environ.get('TAVILY_API_KEY')
    
    # 如果没有API密钥，提示用户输入
    if not tavily_api_key:
        print("提示：TAVILY_API_KEY环境变量未设置，将请求用户输入")
        try:
            # 使用getpass安全获取API密钥
            tavily_api_key = getpass.getpass("请输入Tavily API密钥：")
            os.environ["TAVILY_API_KEY"] = tavily_api_key
        except Exception as e:
            print(f"获取API密钥失败：{str(e)}")
            print("警告：将使用模拟搜索功能")
            
            # 创建模拟搜索函数
            def mock_search(query):
                return [
                    {"content": f"这是关于'{query}'的模拟搜索结果。", "url": "https://example.com"}
                ]
            
            # 创建模拟搜索工具
            return Tool(
                name="OnlineSearch",
                func=mock_search,
                description="用于搜索最新的网络信息，当你需要最新的、实时的或者知识库中没有的信息时使用此工具"
            )
    
    try:
        print("已成功配置Tavily在线搜索功能")
        
        # 定义搜索包装函数，使用requests直接调用Tavily API
        def search_wrapper(query):
            try:
                app_logger.info(f"🌐 开始在线搜索: '{query}'")
                
                # Tavily API的基础URL
                url = "https://api.tavily.com/search"
                app_logger.info(f"🔗 目标API: {url}")
                
                # 检查API密钥是否为空
                if not tavily_api_key:
                    app_logger.error("❌ TAVILY_API_KEY未设置")
                    return "错误：TAVILY_API_KEY未设置，请确保环境变量已正确配置或通过提示输入API密钥。"
                
                # 准备请求参数
                payload = {
                    "api_key": tavily_api_key,
                    "query": query,
                    "search_depth": "basic",  # 基础搜索深度
                    "max_results": 3,  # 返回3个结果
                    "include_answer": False,  # 不包含直接回答
                    "include_raw_content": False,  # 不包含原始内容
                    "include_images": False  # 不包含图片
                }
                app_logger.info(f"📋 搜索参数: {payload}")
                
                # 发送POST请求
                app_logger.info("🚀 正在发送搜索请求...")
                response = requests.post(url, json=payload)
                app_logger.info(f"📡 收到响应，状态码: {response.status_code}")
                
                # 检查响应状态
                if response.status_code != 200:
                    app_logger.error(f"❌ 搜索请求失败，状态码: {response.status_code}")
                    # 更安全地显示API密钥信息，避免泄露完整密钥
                    if len(tavily_api_key) > 10:
                        api_key_display = f"{tavily_api_key[:5]}...{tavily_api_key[-5:]}"
                    else:
                        api_key_display = "密钥长度不足，无法安全显示"
                    app_logger.error(f"🔑 API密钥检查: {api_key_display}")
                    return f"搜索请求失败，状态码：{response.status_code}，错误信息：{response.text}，API密钥检查：{api_key_display}"
                
                # 解析响应JSON
                try:
                    app_logger.info("📄 正在解析搜索结果...")
                    results = response.json()
                    app_logger.info("✅ JSON解析成功")
                except json.JSONDecodeError as e:
                    app_logger.error(f"❌ JSON解析失败: {str(e)}")
                    return f"无法解析搜索结果：{response.text}"
                
                # 提取结果列表
                if "results" not in results:
                    app_logger.error("❌ 搜索结果格式不正确，缺少'results'字段")
                    return f"搜索结果格式不正确，缺少'results'字段"
                
                app_logger.info(f"📊 找到 {len(results['results'])} 个搜索结果")
                
                # 格式化结果
                app_logger.info("📋 开始格式化搜索结果...")
                formatted_results = []
                for i, result in enumerate(results["results"], 1):
                    formatted_result = {
                        "content": result.get("content", ""),
                        "url": result.get("url", ""),
                        "title": result.get("title", "")
                    }
                    formatted_results.append(formatted_result)
                    app_logger.info(f"📄 结果 {i}: {formatted_result['title'][:50]}...")
                
                app_logger.info(f"🎯 在线搜索完成，返回 {len(formatted_results)} 个格式化结果")
                return formatted_results
            except requests.RequestException as e:
                app_logger.error(f"❌ 搜索请求出错: {str(e)}")
                return f"搜索请求出错：{str(e)}"
            except Exception as e:
                app_logger.error(f"❌ 搜索出错: {str(e)}")
                return f"搜索出错：{str(e)}。请检查TAVILY_API_KEY是否正确设置。"
        
        # 创建在线搜索工具
        online_search_tool = Tool(
            name="OnlineSearch",
            func=search_wrapper,
            description="用于搜索最新的网络信息，当你需要最新的、实时的或者知识库中没有的信息时使用此工具"
        )
        
        return online_search_tool
    except Exception as e:
        print(f"创建Tavily搜索工具失败：{str(e)}")
        print("警告：将使用模拟搜索功能")
        
        # 创建模拟搜索函数
        def mock_search(query):
            return [
                {"content": f"这是关于'{query}'的模拟搜索结果。", "url": "https://example.com"}
            ]
        
        # 创建模拟搜索工具
        return Tool(
            name="OnlineSearch",
            func=mock_search,
            description="用于搜索最新的网络信息，当你需要最新的、实时的或者知识库中没有的信息时使用此工具"
        )
def create_online_search_tool_v2():
    """创建一个可以进行在线搜索的工具"""
    # 尝试获取TAVILY API密钥
    tavily_api_key = os.environ.get('TAVILY_API_KEY')
    
    # 如果没有API密钥，提示用户输入
    if not tavily_api_key:
        print("提示：TAVILY_API_KEY环境变量未设置clear，将请求用户输入")
        try:
            # 使用getpass安全获取API密钥
            tavily_api_key = getpass.getpass("请输入Tavily API密钥：")
            os.environ["TAVILY_API_KEY"] = tavily_api_key
        except Exception as e:
            print(f"获取API密钥失败：{str(e)}")
            print("警告：将使用模拟搜索功能")
            
            # 创建模拟搜索函数
            def mock_search(query):
                return [
                    {"content": f"这是关于'{query}'的模拟搜索结果。", "url": "https://example.com"}
                ]
            
            # 创建模拟搜索工具
            return Tool(
                name="OnlineSearchV2",
                func=mock_search,
                description="使用无头浏览器访问Bing搜索网站，用于搜索最新的网络信息，当你需要最新的、实时的或者知识库中没有的信息时使用此工具"
            )
    
    try:
        print("已成功配置Tavily在线搜索功能")
        
        # 定义搜索包装函数，使用requests直接调用Tavily API
        def search_wrapper(query):
            try:
                # Tavily API的基础URL
                url = "https://api.tavily.com/search"
                
                # 检查API密钥是否为空
                if not tavily_api_key:
                    return "错误：TAVILY_API_KEY未设置，请确保环境变量已正确配置或通过提示输入API密钥。"
                
                # 准备请求参数
                payload = {
                    "api_key": tavily_api_key,
                    "query": query,
                    "search_depth": "basic",  # 基础搜索深度
                    "max_results": 5,  # 返回5个结果
                    "include_answer": False,  # 不包含直接回答
                    "include_raw_content": False,  # 不包含原始内容
                    "include_images": False  # 不包含图片
                }
                
                # 发送POST请求
                response = requests.post(url, json=payload)
                
                # 检查响应状态
                if response.status_code != 200:
                    # 更安全地显示API密钥信息，避免泄露完整密钥
                    if len(tavily_api_key) > 10:
                        api_key_display = f"{tavily_api_key[:5]}...{tavily_api_key[-5:]}"
                    else:
                        api_key_display = "密钥长度不足，无法安全显示"
                    return f"搜索请求失败，状态码：{response.status_code}，错误信息：{response.text}，API密钥检查：{api_key_display}"
                
                # 解析响应JSON
                try:
                    results = response.json()
                except json.JSONDecodeError:
                    return f"无法解析搜索结果：{response.text}"
                
                # 提取结果列表
                if "results" not in results:
                    return f"搜索结果格式不正确，缺少'results'字段"
                
                # 格式化结果
                formatted_results = []
                for i, result in enumerate(results["results"]):
                    formatted_results.append({
                        "content": result.get("content", ""),
                        "url": result.get("url", ""),
                        "title": result.get("title", ""),
                        "published_date": "",
                        "score": 1.0 - (i * 0.1),  # 简单评分，结果越靠前分数越高
                        "is_direct_answer": False
                    })
                
                return formatted_results
            except requests.RequestException as e:
                return f"搜索请求出错：{str(e)}"
            except Exception as e:
                return f"搜索出错：{str(e)}。请检查TAVILY_API_KEY是否正确设置。"
        
        # 创建在线搜索工具
        online_search_tool = Tool(
            name="OnlineSearchV2",
            func=search_wrapper,
            description="使用Tavily API进行搜索，用于搜索最新的网络信息，当你需要最新的、实时的或者知识库中没有的信息时使用此工具"
        )
        
        return online_search_tool
    except Exception as e:
        print(f"创建Tavily搜索工具失败：{str(e)}")
        print("警告：将使用模拟搜索功能")
        
        # 创建模拟搜索函数
        def mock_search(query):
            return [
                {"content": f"这是关于'{query}'的模拟搜索结果。", "url": "https://example.com"}
            ]
        
        # 创建模拟搜索工具
        return Tool(
            name="OnlineSearchV2",
            func=mock_search,
            description="使用无头浏览器访问Bing搜索网站，用于搜索最新的网络信息，当你需要最新的、实时的或者知识库中没有的信息时使用此工具"
        )

# 知识库工具（向量数据库）
def create_knowledge_base_tool():
    """创建一个可以将数据存储在向量数据库并进行检索的工具"""
    # 从环境变量获取模型名称
    embedding_model_name = os.getenv("EMBEDDING_MODEL_NAME")
    rerank_model_name = os.getenv("RERANK_MODEL_NAME")
    
    # 初始化嵌入模型 - 添加更多备用选项和本地模型支持
    # 注意：当前版本的langchain_huggingface可能会显示FutureWarning: `resume_download` is deprecated
    # 这是一个警告，不影响功能正常运行
    embedding_models = [
        "sentence-transformers/all-MiniLM-L6-v2",
        "paraphrase-multilingual-MiniLM-L12-v2", 
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "sentence-transformers/distiluse-base-multilingual-cased"
    ]
    
    embeddings = None
    for model_name in embedding_models:
        try:
            print(f"尝试加载嵌入模型: {model_name}")
            embeddings = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={'device': 'cpu'},
                cache_folder="./models_cache"  # 使用cache目录存放模型
            )
            print(f"成功加载嵌入模型: {model_name}")
            break
        except Exception as e:
            app_logger.warning(f"无法加载嵌入模型 {model_name}: {str(e)}")
            print(f"警告：无法加载嵌入模型 {model_name}。错误信息：{str(e)}")
            continue
    
    if embeddings is None:
        app_logger.error("所有嵌入模型都无法加载")
        print("错误：所有嵌入模型都无法加载。请检查网络连接或尝试使用本地模型。")
        print("建议：")
        print("1. 检查网络连接")
        print("2. 尝试使用VPN")
        print("3. 手动下载模型到本地")
        raise Exception("无法加载任何嵌入模型")
    
    # 初始化重排模型 - 使用公开可用的模型
    try:
        reranker = CrossEncoder(rerank_model_name, device='cpu')
    except Exception as e:
        app_logger.warning(f"警告：无法加载重排模型 {rerank_model_name}，错误：{str(e)}")
        app_logger.info("将使用简单相似度检索，不进行重排")
        # 设置一个标志，表示重排模型不可用
        reranker = None
    
    # 初始化向量数据库
    # 如果向量数据库文件不存在，则创建新的
    # 从环境变量获取路径，数据存储在backend/data目录下
    faiss_index_path = os.getenv("FAISS_INDEX_PATH", "./data/index.faiss")
    # faiss_index_path = os.getenv("FAISS_INDEX_PATH")
    # 从FAISS_INDEX_PATH提取目录路径
    vectorstore_path = os.path.dirname(faiss_index_path)
    index_faiss_path = faiss_index_path
    
    # 确保vectorstore_faiss目录存在
    if not os.path.exists(vectorstore_path):
        os.makedirs(vectorstore_path)
    
    # 检查index.faiss文件是否存在
    if os.path.exists(index_faiss_path):
        try:
            vectorstore = FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)
        except Exception as e:
            app_logger.warning(f"警告：加载向量数据库失败，将创建新的数据库。错误：{str(e)}")
            # 创建新的向量数据库
            vectorstore = FAISS.from_texts(["Placeholder text"], embeddings)
            vectorstore.save_local(vectorstore_path)
    else:
        # 创建空的向量数据库
        vectorstore = FAISS.from_texts(["Placeholder text"], embeddings)
        vectorstore.save_local(vectorstore_path)
    
    # 文档处理函数
    def process_and_store_documents(documents: list):
        """处理文档并存储到向量数据库"""
        app_logger.info(f"📚 开始处理文档存储: 共 {len(documents)} 个文档")
        
        # 分割文档
        app_logger.info("✂️ 初始化文档分割器")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        app_logger.info("✅ 文档分割器初始化完成")
        
        # 分割所有文档并添加元数据
        app_logger.info("📝 开始分割文档并提取元数据")
        all_chunks = []
        all_metadatas = []
        for i, doc in enumerate(documents):
            app_logger.info(f"📄 处理文档 {i+1}/{len(documents)}")
            
            # 检查文档类型并提取内容
            if isinstance(doc, dict):
                # 如果是字典格式，提取相关字段
                content = doc.get("description", "")
                title = doc.get("title", f"Document_{i}")
                tags = doc.get("tags", "")
                pub_date = doc.get("pub_date", "")
                author = doc.get("author", "")
                app_logger.info(f"📋 字典格式文档: {title[:50]}...")
            else:
                # 如果是Document对象，提取属性
                content = doc.description if hasattr(doc, 'description') else str(doc)
                title = doc.title if hasattr(doc, 'title') else f"Document_{i}"
                tags = doc.tags if hasattr(doc, 'tags') else ""
                pub_date = doc.pub_date.isoformat() if hasattr(doc, 'pub_date') and doc.pub_date is not None else ""
                author = doc.author if hasattr(doc, 'author') else ""
                app_logger.info(f"📋 Document对象: {title[:50]}...")
            
            # 分割文档内容
            app_logger.info(f"✂️ 分割文档内容，长度: {len(content)} 字符")
            chunks = text_splitter.split_text(content)
            app_logger.info(f"📊 分割完成，生成 {len(chunks)} 个片段")
            
            # 为每个文档片段添加元数据
            metadatas = [{
                "source": f"document_{i}", 
                "chunk": j, 
                "title": title,
                "tags": tags,
                "pub_date": pub_date,
                "author": author,
            } for j in range(len(chunks))]
            all_chunks.extend(chunks)
            all_metadatas.extend(metadatas)
            app_logger.info(f"✅ 文档 {i+1} 处理完成")
        
        # 如果向量数据库中只有占位符文本，则创建新的向量数据库
        app_logger.info("🔍 检查向量数据库状态...")
        try:
            # 获取第一个文档ID
            first_doc_id = list(vectorstore.index_to_docstore_id.values())[0]
            first_doc = vectorstore.docstore.search(first_doc_id)
            is_placeholder = len(vectorstore.index_to_docstore_id) == 1 and "Placeholder text" in str(first_doc)
            app_logger.info(f"📊 向量数据库状态: 占位符={is_placeholder}, 文档数={len(vectorstore.index_to_docstore_id)}")
        except (IndexError, KeyError, AttributeError) as e:
            # 如果获取第一个文档时出错，假设不是占位符
            app_logger.warning(f"⚠️ 检查占位符文本时出错: {str(e)}")
            is_placeholder = False
            
        if is_placeholder:
            app_logger.info("🔄 检测到占位符文本，创建新的向量数据库")
            # 创建新的向量数据库，不包含占位符文本
            new_vectorstore = FAISS.from_texts(all_chunks, embeddings, metadatas=all_metadatas)
            # 替换原来的向量数据库
            vectorstore.index_to_docstore_id = new_vectorstore.index_to_docstore_id
            vectorstore.docstore = new_vectorstore.docstore
            vectorstore.index = new_vectorstore.index
            app_logger.info("✅ 新向量数据库创建完成")
        else:
            app_logger.info("➕ 向现有向量数据库添加文档")
            # 添加到向量数据库（包含元数据）
            vectorstore.add_texts(all_chunks, all_metadatas)
            app_logger.info("✅ 文档添加完成")
        
        # 保存向量数据库到环境变量指定的路径
        app_logger.info(f"💾 保存向量数据库到: {vectorstore_path}")
        vectorstore.save_local(vectorstore_path)
        app_logger.info("✅ 向量数据库保存完成")
        
        result_message = f"成功处理并存储了{len(all_chunks)}个文档片段到向量数据库"
        app_logger.info(f"🎯 文档存储完成: {result_message}")
        return result_message
    
    # 检索函数
    def retrieve_from_knowledge_base(query, k=3, rerank=True):
        """从向量数据库中检索最相关的文档"""
        app_logger.info(f"🔍 开始从向量数据库检索: '{query}'")
        app_logger.info(f"📊 检索参数: k={k}, rerank={rerank}")
        
        # 获取初始检索结果
        if rerank and reranker is not None:
            # 为了重排需要获取更多结果
            initial_k = k * 3
            app_logger.info(f"🔄 启用重排模式，初始检索数量: {initial_k}")
        else:
            initial_k = k
            # 如果没有重排模型或不进行重排，则不进行额外处理
            rerank = False
            app_logger.info(f"⚡ 直接检索模式，检索数量: {initial_k}")
            
        app_logger.info("📚 正在执行向量相似度搜索...")
        results = vectorstore.similarity_search(query, k=initial_k)
        app_logger.info(f"✅ 向量搜索完成，获得 {len(results)} 个初始结果")
        
        # 使用重排模型对结果进行排序（仅在模型可用时）
        if rerank and results and reranker is not None:
            try:
                app_logger.info("🔄 开始重排模型处理...")
                # 准备用于重排的文本对
                sentence_pairs = [[query, result.page_content] for result in results]
                app_logger.info(f"📝 准备重排文本对，共 {len(sentence_pairs)} 对")
                
                # 获取重排分数
                app_logger.info("🧠 正在计算重排分数...")
                scores = reranker.predict(sentence_pairs)
                app_logger.info(f"📊 重排分数计算完成: {scores}")
                
                # 按分数降序排序
                results_with_scores = list(zip(results, scores))
                results_with_scores.sort(key=lambda x: x[1], reverse=True)
                app_logger.info("🔢 按重排分数排序完成")
                
                # 只保留前k个结果
                results = [result for result, _ in results_with_scores[:k]]
                app_logger.info(f"✅ 重排完成，保留前 {k} 个最相关结果")
            except Exception as e:
                app_logger.warning(f"⚠️ 重排过程出错，将使用原始检索结果。错误：{str(e)}")
                # 确保results仍然是可迭代的，并且保持原始结果
                if not isinstance(results, list):
                    # 如果results不是列表，尝试从vectorstore重新获取
                    try:
                        app_logger.info("🔄 尝试重新获取检索结果...")
                        results = vectorstore.similarity_search(query, k=k)
                        app_logger.info(f"✅ 重新获取成功，获得 {len(results)} 个结果")
                    except Exception as e2:
                        app_logger.error(f"❌ 重新获取失败: {str(e2)}")
                        results = []
                # 如果results仍然不是列表，设置为空列表
                if not isinstance(results, list):
                    results = []
        else:
            # 如果没有重排或重排模型不可用，确保results是列表
            if not isinstance(results, list):
                results = []
            app_logger.info("⚡ 跳过重排，使用原始检索结果")
        
        # 确保results是列表并且有内容
        if not isinstance(results, list):
            results = []
        elif len(results) == 0:
            # 如果results为空，尝试重新获取
            try:
                app_logger.warning("⚠️ 检索结果为空，尝试重新获取...")
                results = vectorstore.similarity_search(query, k=k)
                app_logger.info(f"✅ 重新获取成功，获得 {len(results)} 个结果")
            except Exception as e:
                app_logger.error(f"❌ 重新获取失败: {str(e)}")
                results = []
        
        # 格式化结果
        app_logger.info("📋 开始格式化检索结果...")
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append({
                "id": i,
                "content": result.page_content,
                "metadata": result.metadata
            })
        
        app_logger.info(f"🎯 向量数据库检索完成，返回 {len(formatted_results)} 个格式化结果")
        return formatted_results
    
    # 创建工具 - 进一步调整函数实现以处理不同的数据类型
    def knowledge_base_func(action: str, documents: list = None, query=None, k: int = 3, rerank: bool = True):
        """处理知识库工具的输入数据
        
        Args:
            action: 操作类型，支持'store'和'retrieve'
            documents: 对于'store'操作，是Document对象列表或文档字典列表
            query: 对于'retrieve'操作，是查询字符串
            k: 对于'retrieve'操作，返回结果数量，默认为3
            rerank: 对于'retrieve'操作，是否启用结果重排，默认为True
        """
        app_logger.info(f"🔧 知识库工具调用: action={action}")
        
        if action == "store":
            app_logger.info(f"📚 存储操作: 处理 {len(documents) if documents else 0} 个文档")
            # 检查documents参数是否为Document对象列表
            if documents and len(documents) > 0 and hasattr(documents[0], 'title'):
                app_logger.info("🔄 检测到Document对象列表，转换为字典格式")
                # 如果是Document对象列表，转换为字典格式
                from models.document import Document
                document_dicts = []
                for doc in documents:
                    if isinstance(doc, Document):
                        doc_dict = {
                            "title": doc.title,
                            "description": doc.description,
                            "tags": doc.tags,
                            "pub_date": doc.pub_date,
                            "author": doc.author
                        }
                        document_dicts.append(doc_dict)
                    else:
                        # 如果已经是字典格式，直接添加
                        document_dicts.append(doc)
                app_logger.info(f"✅ 转换完成，共 {len(document_dicts)} 个文档")
                return process_and_store_documents(document_dicts)
            else:
                app_logger.info("📄 直接处理字典格式文档")
                # 如果是字典列表，直接处理
                return process_and_store_documents(documents)
        elif action == "retrieve":
            app_logger.info(f"🔍 检索操作: query='{query}', k={k}, rerank={rerank}")
            return retrieve_from_knowledge_base(query, k, rerank)
        elif action == "cluster_analysis":
            app_logger.info("📊 聚类分析操作")
            return knowledge_base_cluster_analysis()
        else:
            app_logger.error(f"❌ 不支持的操作: {action}")
            return f"不支持的操作：{action}"
    
    knowledge_base_tool = StructuredTool.from_function(
        func=knowledge_base_func,
        name="KnowledgeBase",
        description="用于处理和检索向量数据库中的知识，支持存储文档(store)和检索信息(retrieve)两种操作"
    )
    
    return knowledge_base_tool

# 生成聚类标签的函数
def generate_cluster_label(keywords):
    """
    根据关键词生成聚类的描述性标签
    
    Args:
        keywords (list): 聚类的关键词列表
        
    Returns:
        str: 聚类的描述性标签
    """
    if not keywords:
        return "未分类"
    
    # 常见主题关键词映射
    topic_keywords = {
        "政治": ["政府", "国家", "总统", "领导人", "选举", "政策", "议会", "党派", "政治", "外交"],
        "经济": ["经济", "金融", "市场", "股票", "投资", "贸易", "货币", "银行", "财政", "GDP"],
        "科技": ["科技", "技术", "人工智能", "数据", "互联网", "软件", "计算机", "数字", "创新", "研发"],
        "军事": ["军事", "军队", "国防", "武器", "战争", "冲突", "安全", "演习", "基地", "武装"],
        "社会": ["社会", "文化", "教育", "健康", "医疗", "环境", "气候", "人口", "社区", "民生"],
        "体育": ["体育", "足球", "篮球", "比赛", "运动员", "奥运", "世界杯", "冠军", "联赛", "教练"],
        "娱乐": ["娱乐", "电影", "音乐", "明星", "演员", "歌手", "节目", "表演", "艺术", "媒体"],
        "国际": ["国际", "联合国", "全球", "世界", "外交", "合作", "峰会", "协议", "组织", "多边"],
        "灾难": ["灾难", "地震", "洪水", "火灾", "事故", "救援", "伤亡", "损失", "紧急", "危险"],
        "犯罪": ["犯罪", "案件", "警察", "调查", "逮捕", "审判", "法律", "法院", "嫌疑", "证据"]
    }
    
    # 计算每个主题的匹配度
    topic_scores = {}
    for topic, topic_kw in topic_keywords.items():
        score = sum(1 for kw in keywords if kw in topic_kw)
        if score > 0:
            topic_scores[topic] = score
    
    # 如果没有匹配的主题，使用前两个关键词作为标签
    if not topic_scores:
        return f"{keywords[0]}相关" if len(keywords) >= 1 else "未分类"
    
    # 选择得分最高的主题
    best_topic = max(topic_scores, key=topic_scores.get)
    
    # 如果有多个关键词匹配，可以添加更具体的描述
    if topic_scores[best_topic] >= 2:
        return f"{best_topic}相关"
    else:
        # 如果只有一个关键词匹配，添加该关键词作为具体描述
        matched_keyword = next((kw for kw in keywords if kw in topic_keywords[best_topic]), None)
        if matched_keyword:
            return f"{best_topic}({matched_keyword})"
        else:
            return f"{best_topic}相关"


# 知识库数据聚类分析报告，展示关键前10分布
def knowledge_base_cluster_analysis():
    """对知识库中的数据进行聚类分析，并展示关键前10分布"""
    try:
        app_logger.info("开始知识库数据聚类分析")
        
        # 从环境变量获取模型名称和路径
        embedding_model_name = os.getenv("EMBEDDING_MODEL_NAME")
        faiss_index_path = os.getenv("FAISS_INDEX_PATH")
        vectorstore_path = os.path.dirname(faiss_index_path)
        
        # 初始化嵌入模型
        embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model_name,
            model_kwargs={'device': 'cpu'}
        )
        
        # 加载向量数据库
        if os.path.exists(faiss_index_path):
            try:
                vectorstore = FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)
                app_logger.info("成功加载向量数据库")
            except Exception as e:
                app_logger.error(f"加载向量数据库失败：{str(e)}")
                return {"error": f"加载向量数据库失败：{str(e)}"}
        else:
            app_logger.error("向量数据库文件不存在")
            return {"error": "向量数据库文件不存在"}
        
        # 获取向量数据库中的所有文档
        # 由于FAISS不直接提供获取所有文档的方法，我们需要通过索引来获取
        try:
            # 获取文档向量
            docstore = vectorstore.docstore
            index_to_docstore_id = vectorstore.index_to_docstore_id
            
            # 提取所有文档内容和元数据
            documents = []
            for idx, doc_id in enumerate(index_to_docstore_id.values()):
                try:
                    doc = docstore.search(doc_id)
                    if doc is not None:
                        # 检查doc是Document对象还是字符串
                        if hasattr(doc, 'page_content'):
                            # 这是一个Document对象
                            documents.append({
                                "content": doc.page_content,
                                "metadata": doc.metadata if hasattr(doc, 'metadata') else {}
                            })
                        else:
                            # 这是一个字符串或其他对象
                            documents.append({
                                "content": str(doc),
                                "metadata": {}
                            })
                except (KeyError, AttributeError) as e:
                    # 如果文档ID不存在于docstore中，跳过该文档
                    continue
            
            app_logger.info(f"从向量数据库中提取了{len(documents)}个文档")
            
            if len(documents) < 10:
                app_logger.warning("文档数量不足10个，聚类分析结果可能不准确")
                
            # 文本预处理函数
            def preprocess_text(text, tags=None):
                import re
                from bs4 import BeautifulSoup
                
                # 去除HTML标签
                if '<' in text and '>' in text:
                    soup = BeautifulSoup(text, 'html.parser')
                    text = soup.get_text()
                
                # 去除URL
                text = re.sub(r'https?://\S+|www\.\S+', '', text)
                
                # 去除特殊字符和数字，保留中英文
                text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z\s]', ' ', text)

                # 额外移除常见HTML属性/无意义标记及其组合（如 dir、ltr、fr 以及包含它们的短语）
                banned_tokens = [
                    'dir', 'ltr', 'rtl', 'align', 'center', 'left', 'right', 'nbsp', 'nbspnbsp',
                    'figcaption', 'caption', 'blockquote', 'figure', 'video', 'pagevideo', 'poster', 'style'
                ]
                # 移除独立出现的禁用词
                pattern_single = r'\b(' + '|'.join(banned_tokens) + r')\b'
                text = re.sub(pattern_single, ' ', text, flags=re.IGNORECASE)
                # 移除含禁用词的二元短语（例："dir ltr", "ebmt dir", "bbc fr"）
                pattern_bigram = r'\b(?:\w+\s+)?(' + '|'.join(banned_tokens) + r')(?:\s+\w+)?\b'
                text = re.sub(pattern_bigram, ' ', text, flags=re.IGNORECASE)
                
                # 处理tags字段
                if tags and isinstance(tags, str):
                    # 将tags按逗号分割，并过滤掉空字符串
                    tag_words = [tag.strip() for tag in tags.split(',') if tag.strip()]
                    # 将tags添加到文本中，增加权重（重复3次）
                    if tag_words:
                        text = text + ' ' + ' '.join(tag_words * 3)
                
                # 去除多余空格
                text = re.sub(r'\s+', ' ', text).strip()
                
                return text
            
            # 预处理所有文档内容，包括tags字段
            processed_contents = []
            for doc in documents:
                # 获取tags字段，如果metadata中不存在则为空字符串
                tags = doc.get("metadata", {}).get("tags", "")
                # 预处理文本，包括tags
                processed_content = preprocess_text(doc["content"], tags)
                processed_contents.append(processed_content)
            
            # 使用TF-IDF向量化文档，支持中英文
            # 添加自定义停用词
            custom_stop_words = [
                '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '作者', '笔者', '日电', '她说', '另有', '今年', '去年', '明年', '早些',
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'am', 'http', 'https', 'www', 'com', 'cn', 'org', 'net', 'href', 'target', 'blank', 'src', 'img', 'figure', 'figcaption', 'div', 'class', 'style', 'id', 'title', 'alt', 'author', 'margin', 'auto', 'display', 'block', 'float', 'none', 'width', 'height', 'padding', 'border', 'background', 'color', 'font', 'text', 'align', 'center', 'left', 'right', 'top', 'bottom', 'position', 'relative', 'absolute', 'fixed', 'clear', 'overflow', 'hidden', 'visible', 'scroll', 'z-index', 'opacity', 'transition', 'transform', 'box-shadow', 'border-radius', 'outline', 'cursor', 'pointer', 'box', 'index', 'radius', 'shadow',
                'as', 'it', 'than', 'said', 'say', 'new', 'old', 'up', 'more', 'he', 'she', 'him', 'her', 'me', 'my', 'mine'
            ]
            
            vectorizer = TfidfVectorizer(
                max_features=2000,  # 增加特征数量
                stop_words=custom_stop_words,
                ngram_range=(1, 2),  # 添加二元语法
                min_df=2,  # 最小文档频率
                max_df=0.8,  # 最大文档频率
                sublinear_tf=True  # 使用子线性TF缩放
            )
            tfidf_matrix = vectorizer.fit_transform(processed_contents)
            
            # 使用UMAP降维和HDBSCAN聚类（更先进的聚类方法）
            try:
                # 尝试导入UMAP和HDBSCAN
                import umap
                import hdbscan
                use_advanced_clustering = True
                app_logger.info("使用UMAP降维和HDBSCAN聚类")
            except ImportError:
                use_advanced_clustering = False
                app_logger.warning("未安装UMAP或HDBSCAN，使用传统K-means聚类")
            
            if use_advanced_clustering:
                # 使用UMAP进行降维
                # 优化UMAP参数，提高降维质量
                n_neighbors = min(15, max(5, int(len(documents) * 0.3)))
                if n_neighbors < 2:
                    n_neighbors = 2
                    
                n_components = min(50, len(documents) - 1, len(documents) // 2)
                if n_components < 2:
                    n_components = 2
                    
                # 优化UMAP参数配置
                umap_params = {
                    'n_components': n_components,  # 降维后的维度
                    'n_neighbors': n_neighbors,  # 邻居数量
                    'min_dist': 0.05,  # 减小最小距离，使聚类更紧凑
                    'metric': 'cosine',  # 使用余弦相似度，更适合文本数据
                    'random_state': 42,
                    'transform_seed': 42,
                    'spread': 1.0,  # 增加扩展参数，使点分布更均匀
                    'local_connectivity': 2,  # 增加局部连通性
                    'repulsion_strength': 1.0,  # 增加排斥强度
                    'negative_sample_rate': 5,  # 增加负采样率
                }
                
                reducer = umap.UMAP(**umap_params)
                
                # 如果数据集很小，直接使用TF-IDF矩阵而不降维
                if len(documents) <= 10:
                    app_logger.info("数据集太小，跳过UMAP降维，直接使用TF-IDF矩阵")
                    embedding = tfidf_matrix.toarray()
                else:
                    try:
                        embedding = reducer.fit_transform(tfidf_matrix)
                        app_logger.info(f"UMAP降维完成，原始维度: {tfidf_matrix.shape[1]}，降维后维度: {embedding.shape[1]}")
                        
                        # 对降维后的数据进行标准化处理
                        from sklearn.preprocessing import StandardScaler
                        scaler = StandardScaler()
                        embedding = scaler.fit_transform(embedding)
                        
                        app_logger.info("降维数据标准化完成")
                    except Exception as e:
                        app_logger.warning(f"UMAP降维失败: {str(e)}，使用TF-IDF矩阵作为替代")
                        embedding = tfidf_matrix.toarray()
            
            if use_advanced_clustering:
                # 使用HDBSCAN进行聚类
                # 降低参数要求，使聚类更容易形成
                min_cluster_size = max(2, int(len(documents) * 0.03))  # 降低最小聚类大小
                min_samples = max(1, int(len(documents) * 0.01))  # 降低最小样本数
                
                # 尝试不同的聚类选择方法，找到最佳结果
                best_cluster_labels = None
                best_optimal_clusters = 0
                best_silhouette_avg = -1
                
                for cluster_selection in ['eom', 'leaf']:
                    try:
                        clusterer = hdbscan.HDBSCAN(
                            min_cluster_size=min_cluster_size,
                            min_samples=min_samples,
                            metric='euclidean',
                            cluster_selection_method=cluster_selection,
                            prediction_data=True,
                            gen_min_span_tree=True  # 生成最小生成树以提高聚类质量
                        )
                        cluster_labels = clusterer.fit_predict(embedding)
                        
                        # 统计聚类数量（忽略噪声点，标签为-1）
                        unique_labels = set(cluster_labels)
                        if -1 in unique_labels:
                            unique_labels.remove(-1)
                        current_optimal_clusters = len(unique_labels)
                        
                        # 计算轮廓系数（排除噪声点）
                        if current_optimal_clusters > 1:
                            non_noise_indices = [i for i, label in enumerate(cluster_labels) if label != -1]
                            if len(non_noise_indices) > current_optimal_clusters:
                                try:
                                    current_silhouette_avg = silhouette_score(
                                        embedding[non_noise_indices], 
                                        cluster_labels[non_noise_indices]
                                    )
                                    
                                    # 如果当前聚类结果更好，则保存
                                    if current_silhouette_avg > best_silhouette_avg:
                                        best_silhouette_avg = current_silhouette_avg
                                        best_optimal_clusters = current_optimal_clusters
                                        best_cluster_labels = cluster_labels.copy()
                                except Exception as e:
                                    app_logger.warning(f"计算轮廓系数失败: {str(e)}")
                                    continue
                    except Exception as e:
                        app_logger.warning(f"聚类方法 {cluster_selection} 失败: {str(e)}")
                        continue
                
                # 如果没有找到有效的聚类结果，使用默认方法
                if best_cluster_labels is None:
                    clusterer = hdbscan.HDBSCAN(
                        min_cluster_size=min_cluster_size,
                        min_samples=min_samples,
                        metric='euclidean',
                        cluster_selection_method='eom',
                        prediction_data=True
                    )
                    best_cluster_labels = clusterer.fit_predict(embedding)
                    
                    # 统计聚类数量
                    unique_labels = set(best_cluster_labels)
                    if -1 in unique_labels:
                        unique_labels.remove(-1)
                    best_optimal_clusters = len(unique_labels)
                    best_silhouette_avg = 0
                
                cluster_labels = best_cluster_labels
                optimal_clusters = best_optimal_clusters
                silhouette_avg = best_silhouette_avg
                
                app_logger.info(f"HDBSCAN聚类完成，发现{optimal_clusters}个聚类，轮廓系数: {silhouette_avg:.4f}")
                
                # 如果聚类数量过多，尝试合并小聚类
                if optimal_clusters > 60:
                    app_logger.info("聚类数量过多，尝试合并小聚类")
                    # 统计每个聚类的文档数量
                    cluster_counts = Counter(cluster_labels)
                    # 找出文档数量最少的聚类
                    small_clusters = [cid for cid, count in cluster_counts.items() 
                                     if cid != -1 and count < max(1, len(documents) * 0.02)]
                    
                    if small_clusters:
                        # 将小聚类合并到最近的聚类
                        for small_cluster_id in small_clusters:
                            # 找到小聚类的中心点
                            small_cluster_indices = [i for i, label in enumerate(cluster_labels) if label == small_cluster_id]
                            if small_cluster_indices:
                                small_cluster_center = embedding[small_cluster_indices].mean(axis=0)
                                
                                # 找到最近的聚类
                                min_distance = float('inf')
                                nearest_cluster = -1
                                
                                for cluster_id in set(cluster_labels):
                                    if cluster_id != -1 and cluster_id != small_cluster_id:
                                        cluster_indices = [i for i, label in enumerate(cluster_labels) if label == cluster_id]
                                        if cluster_indices:
                                            cluster_center = embedding[cluster_indices].mean(axis=0)
                                            distance = np.linalg.norm(small_cluster_center - cluster_center)
                                            if distance < min_distance:
                                                min_distance = distance
                                                nearest_cluster = cluster_id
                                
                                # 合并聚类
                                if nearest_cluster != -1:
                                    for idx in small_cluster_indices:
                                        cluster_labels[idx] = nearest_cluster
                                    app_logger.info(f"将聚类{small_cluster_id}合并到聚类{nearest_cluster}")
                        
                        # 重新统计聚类数量
                        unique_labels = set(cluster_labels)
                        if -1 in unique_labels:
                            unique_labels.remove(-1)
                        optimal_clusters = len(unique_labels)
                        
                        # 重新计算轮廓系数
                        if optimal_clusters > 1:
                            non_noise_indices = [i for i, label in enumerate(cluster_labels) if label != -1]
                            if len(non_noise_indices) > optimal_clusters:
                                try:
                                    silhouette_avg = silhouette_score(
                                        embedding[non_noise_indices], 
                                        cluster_labels[non_noise_indices]
                                    )
                                except Exception as e:
                                    app_logger.warning(f"重新计算轮廓系数失败: {str(e)}")
                                    silhouette_avg = best_silhouette_avg
                        
                        app_logger.info(f"合并后聚类数量: {optimal_clusters}，轮廓系数: {silhouette_avg:.4f}")
                
            else:
                # 使用传统K-means聚类
                max_possible_clusters = min(15, len(documents) // 2) if len(documents) > 20 else 10
                if max_possible_clusters < 2:
                    max_possible_clusters = 2
                
                # 计算不同聚类数量的轮廓系数
                silhouette_scores = []
                possible_clusters = range(2, min(max_possible_clusters + 1, 11))
                
                for n_clusters in possible_clusters:
                    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                    cluster_labels = kmeans.fit_predict(tfidf_matrix)
                    silhouette_avg = silhouette_score(tfidf_matrix, cluster_labels)
                    silhouette_scores.append(silhouette_avg)
                
                # 选择轮廓系数最大的聚类数量
                optimal_clusters = possible_clusters[silhouette_scores.index(max(silhouette_scores))]
                silhouette_avg = max(silhouette_scores)
                
                # 使用K-means聚类
                kmeans = KMeans(n_clusters=optimal_clusters, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(tfidf_matrix)
                
                app_logger.info(f"K-means聚类完成，聚类数量: {optimal_clusters}，轮廓系数: {silhouette_avg:.4f}")
            
            # 获取聚类标签
            labels = cluster_labels
            
            # 统计每个聚类的文档数量
            cluster_counts = Counter(labels)
            
            # 如果使用HDBSCAN，统计噪声点数量
            if use_advanced_clustering and -1 in cluster_counts:
                noise_count = cluster_counts[-1]
                app_logger.info(f"发现{noise_count}个噪声点（未归类到任何聚类的文档）")
                # 从聚类统计中移除噪声点
                del cluster_counts[-1]
            
            # 提取每个聚类的关键词 - 改进方法
            feature_names = vectorizer.get_feature_names_out()
            cluster_keywords = {}
            
            # 过滤无意义词汇的通用方法
            def is_meaningful_word(word):
                # 1. 基本长度过滤
                if len(word) < 2:
                    return False
                
                # 2. 过滤单字词汇（除非是特定有意义的单字）
                if len(word) == 1 and word not in ['水', '火', '土', '金', '木', '车', '路', '桥', '药', '病', '法', '税', '政', '军', '国']:
                    return False

                # 2.1 任何包含以下子串的词（包括二元短语）直接过滤
                banned_substrings = [
                    'dir', 'ltr', 'rtl', 'align', 'center', 'left', 'right', 'nbsp',
                    'figcaption', 'caption', 'blockquote', 'figure', 'video', 'pagevideo', 'poster', 'style'
                ]
                lower_word = word.lower()
                if any(sub in lower_word for sub in banned_substrings):
                    return False
                
                # 3. 过滤过长词汇（超过15个字符的词汇通常不是好的关键词）
                if len(word) > 15:
                    return False
                
                # 4. 过滤常见无意义后缀
                meaningless_suffixes = ['的', '了', '着', '过', '们', '中', '内', '外', '上', '下', '左', '右', '前', '后', '里', '间', '侧', '边', '面', '头', '尾', '部', '分', '月', '年', '日', '时', '分', '秒', '度', '米', '克', '吨', '个', '只', '条', '张', '件', '种', '类', '型', '式', '样', '等', '级', '数', '量', '比', '率', '值', '价', '钱', '元', '块', '毛']
                if word.endswith(tuple(meaningless_suffixes)):
                    return False
                
                # 5. 过滤常见无意义前缀
                meaningless_prefixes = ['非', '无', '不', '没', '未', '别', '莫', '勿']
                if word.startswith(tuple(meaningless_prefixes)) and len(word) <= 3:
                    return False
                
                # 6. 过滤纯数字或以数字开头的词
                if word.isdigit() or (len(word) > 1 and word[0].isdigit()):
                    return False
                
                # 7. 过滤常见无意义组合词
                meaningless_combinations = [
                    '分左右', '分上下', '分前后', '分内外', '分东西', '分南北', '分大小', '分多少', '分高低', '分长短',
                    '的左右', '的上下', '的前后', '的内外', '的中间', '的旁边', '的附近', '的周围', '的上面', '的下面',
                    '月左右', '年左右', '日左右', '时左右', '分左右', '秒左右', '度左右', '米左右', '克左右', '吨左右',
                    '分左右', '分上下', '分前后', '分内外', '分东西', '分南北', '分大小', '分多少', '分高低', '分长短',
                    '的月', '的年', '的日', '的时', '的分', '的秒', '的度', '的米', '的克', '的吨', '的个', '的只', '的条', '的张',
                    '月的', '年的', '日的', '时的', '分的', '秒的', '度的', '米的', '克的', '吨的', '个的', '只的', '条的', '张的',
                    # 新增的无意义组合
                    '日至', '日说', '并于', '报道', '他说', '日至', '日报道', '日说', '路透社报道', '法新社报道', '彭博社报道', '新华社报道'
                ]
                if word in meaningless_combinations:
                    return False
                
                # 8. 过滤重复字符词（如"啊啊啊"、"哈哈哈"等）
                if len(set(word)) == 1 and len(word) > 2:
                    return False
                
                # 9. 过滤HTML/XML相关词汇
                html_terms = ['href', 'src', 'img', 'div', 'class', 'style', 'id', 'title', 'alt', 'http', 'https', 'www', 'com', 'cn', 'org', 'net', 'target', 'blank', '_blank']
                if word in html_terms:
                    return False
                
                # 10. 过滤网站相关词汇
                website_terms = ['zaobao', 'sg', 'cassette', 'sphdigital', 'image', 'figcapton']
                if word in website_terms:
                    return False
                
                # 11. 过滤常见媒体名称（除非它们是关键词的核心部分）
                media_names = ['路透社', '法新社', '彭博社', '新华社', '美联社', '塔斯社', '共同社']
                if word in media_names and len(word) <= 4:
                    return False
                
                # 12. 过滤时间相关词汇
                time_patterns = [
                    r'\d{1,2}月\d{1,2}日', r'\d{4}年\d{1,2}月', r'\d{1,2}日', r'\d{1,2}月', r'\d{4}年',
                    r'星期[一二三四五六七日]', r'周[一二三四五六七日]', r'礼拜[一二三四五六七日]'
                ]
                import re
                for pattern in time_patterns:
                    if re.match(pattern, word):
                        return False
                
                # 13. 过滤连接词和过渡词
                transition_words = ['然而', '但是', '不过', '因此', '所以', '于是', '另外', '此外', '同时', '其次', '首先', '最后', '总之', '综上', '另外', '此外']
                if word in transition_words:
                    return False
                
                # 14. 过滤常见报道用语
                reporting_phrases = ['据了解', '据报道', '据介绍', '据悉', '据称', '据透露', '据消息', '据观察', '据分析', '据统计']
                if word in reporting_phrases:
                    return False
                
                # 15. 过滤短时间相关词汇
                short_time_phrases = ['天内恢复', '月内完成', '年内实现', '周内解决', '日前', '日后', '月前', '年后']
                if word in short_time_phrases:
                    return False
                
                # 16. 过滤条件连词
                condition_words = ['若', '如果', '假如', '假使', '倘若', '要是', '万一', '只要', '只有', '除非', '一旦', '如果', '若是', '若果', '若使', '若为']
                if word in condition_words:
                    return False
                
                # 17. 过滤以条件连词开头的短语
                condition_prefixes = ['若', '如果', '假如', '假使', '倘若', '要是', '万一', '只要', '只有', '除非', '一旦']
                if any(word.startswith(prefix) for prefix in condition_prefixes):
                    return False
                
                return True
            
            for cluster_id in sorted(cluster_counts.keys()):
                # 获取该聚类的文档索引
                cluster_indices = [idx for idx, label in enumerate(labels) if label == cluster_id]
                
                if not cluster_indices:
                    continue
                
                # 计算该聚类中每个词的平均TF-IDF值
                cluster_tfidf_mean = tfidf_matrix[cluster_indices].mean(axis=0)
                cluster_tfidf_mean = np.array(cluster_tfidf_mean).flatten()
                
                # 提取聚类内所有文档的标题，并增强标题中词汇的权重
                cluster_titles = [documents[i]["metadata"]["title"] for i in cluster_indices if "title" in documents[i]["metadata"]]
                if cluster_titles:
                    # 将所有标题合并为一个文本
                    titles_text = ' '.join(cluster_titles)
                    # 分词并统计标题中的词频
                    title_words = re.findall(r'\b\w+\b', titles_text.lower())
                    title_word_freq = Counter(title_words)
                    
                    # 增强标题中词汇的TF-IDF权重（增加50%的权重）
                    for word, freq in title_word_freq.items():
                        # 找到该词在feature_names中的索引
                        word_indices = [i for i, feature in enumerate(feature_names) if feature == word]
                        for idx in word_indices:
                            if idx < len(cluster_tfidf_mean):
                                cluster_tfidf_mean[idx] *= 1.5
                
                # 获取TF-IDF值最高的前10个关键词
                top_indices = cluster_tfidf_mean.argsort()[-10:][::-1]
                top_keywords = [feature_names[idx] for idx in top_indices if cluster_tfidf_mean[idx] > 0]
                
                # 如果使用HDBSCAN，还可以考虑聚类在降维空间中的密度
                if use_advanced_clustering:
                    # 计算聚类在降维空间中的中心点
                    if 'embedding' in locals():
                        cluster_center = embedding[cluster_indices].mean(axis=0)
                        # 找到距离中心点最近的文档作为代表文档
                        distances = np.linalg.norm(embedding[cluster_indices] - cluster_center, axis=1)
                        representative_doc_idx = cluster_indices[np.argmin(distances)]
                        # 从代表文档中提取额外关键词
                        rep_doc_tfidf = tfidf_matrix[representative_doc_idx].toarray().flatten()
                        rep_top_indices = rep_doc_tfidf.argsort()[-5:][::-1]
                        rep_keywords = [feature_names[idx] for idx in rep_top_indices if rep_doc_tfidf[idx] > 0]
                        # 添加到关键词列表（如果尚未存在）
                        for keyword in rep_keywords:
                            if keyword not in top_keywords and len(top_keywords) < 10:
                                top_keywords.append(keyword)
                
                # 如果关键词不足10个，尝试从聚类中心获取（仅适用于K-means）
                if len(top_keywords) < 10 and not use_advanced_clustering:
                    cluster_center = kmeans.cluster_centers_[cluster_id]
                    additional_indices = cluster_center.argsort()[-(10-len(top_keywords)):][::-1]
                    additional_keywords = [feature_names[idx] for idx in additional_indices if feature_names[idx] not in top_keywords]
                    top_keywords.extend(additional_keywords)
                
                # 如果仍然不足10个，使用聚类内所有文档的高频词补充
                if len(top_keywords) < 10:
                    # 统计聚类内所有文档的词频，包括内容和标题
                    cluster_contents = [documents[i]["content"] for i in cluster_indices]
                    cluster_titles = [documents[i]["metadata"]["title"] for i in cluster_indices if "title" in documents[i]["metadata"]]
                    
                    # 将标题和内容合并，但给标题更高的权重（重复3次）
                    cluster_text = ' '.join(cluster_titles * 3 + cluster_contents)
                    
                    # 分词并统计词频
                    words = re.findall(r'\b\w+\b', cluster_text.lower())
                    word_freq = Counter(words)
                    
                    # 过滤掉停用词和已有关键词
                    custom_stop_words = [
                        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '作者',
                        '笔者',
                        'dir','ltr','fr','the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'am', 'http', 'https', 'www', 'com', 'cn', 'org', 'net', 'href', 'target', 'blank', 'src', 'img', 'figure', 'figcaption', 'div', 'class', 'style', 'id', 'title', 'alt', 'author',
                        'as', 'it', 'than', 'said', 'say', 'new', 'old', 'up', 'more', 'he', 'she', 'him', 'her', 'me', 'my', 'mine'
                    ]
                    
                    filtered_words = [(word, freq) for word, freq in word_freq.most_common() 
                                     if word not in custom_stop_words and word not in top_keywords and is_meaningful_word(word)]
                    
                    # 补充关键词
                    for word, freq in filtered_words:
                        top_keywords.append(word)
                        if len(top_keywords) >= 10:
                            break
                
                # 最终过滤：对已选关键词进行最后一次无意义词过滤
                top_keywords = [word for word in top_keywords if is_meaningful_word(word)]
                
                cluster_keywords[cluster_id] = top_keywords[:10]  # 确保最多10个关键词
                
                # 立即打印当前聚类的关键词，用于评估过滤效果
                print(f"聚类 {cluster_id}: {top_keywords[:10]}")
            
            # 按聚类大小排序
            sorted_clusters = sorted(cluster_counts.items(), key=lambda x: x[1], reverse=True)
            
            # 准备聚类结果
            top_clusters = []
            for cluster_id, count in sorted_clusters[:10]:
                # 获取该聚类的代表性文档
                cluster_docs = [documents[i] for i, label in enumerate(labels) if label == cluster_id]
                
                # 计算聚类在总文档中的占比
                percentage = (count / len(documents)) * 100
                
                # 为聚类生成描述性标签
                cluster_label = generate_cluster_label(cluster_keywords.get(cluster_id, []))
                
                top_clusters.append({
                    "cluster_id": int(cluster_id),
                    "cluster_label": cluster_label,
                    "document_count": count,
                    "percentage": round(percentage, 2),
                    "keywords": cluster_keywords.get(cluster_id, []),
                    "sample_documents": [
                        {
                            "content": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"],
                            "metadata": {
                                "title": doc["metadata"].get("title", ""),
                                "author": doc["metadata"].get("author", ""),
                                "pub_date": doc["metadata"].get("pub_date", ""),
                                "source": doc["metadata"].get("source", ""),
                                "tags": doc["metadata"].get("tags", "")
                            }
                        }
                        for doc in cluster_docs[:3]  # 每个聚类取前3个文档作为样本
                    ]
                })
            
            # 如果使用HDBSCAN，添加噪声点信息
            noise_info = None
            if use_advanced_clustering and -1 in cluster_labels:
                noise_docs = [documents[i] for i, label in enumerate(labels) if label == -1]
                noise_info = {
                    "count": len(noise_docs),
                    "percentage": round((len(noise_docs) / len(documents)) * 100, 2),
                    "sample_documents": [
                        {
                            "content": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"],
                            "metadata": {
                                "title": doc["metadata"].get("title", ""),
                                "author": doc["metadata"].get("author", ""),
                                "pub_date": doc["metadata"].get("pub_date", ""),
                                "source": doc["metadata"].get("source", ""),
                                "tags": doc["metadata"].get("tags", "")
                            }
                        }
                        for doc in noise_docs[:3]  # 取前3个噪声文档作为样本
                    ]
                }
            
            # 生成分析报告
            analysis_report = {
                "total_documents": len(documents),
                "total_clusters": optimal_clusters,
                "analysis_date": str(np.datetime64('now')),
                "top_clusters": top_clusters,
                "cluster_distribution": {
                    str(cluster_id): count for cluster_id, count in sorted_clusters
                },
                "silhouette_score": silhouette_avg,
                "clustering_method": "HDBSCAN with UMAP" if use_advanced_clustering else "K-means",
                "optimization_info": {
                    "original_clusters": max_possible_clusters if not use_advanced_clustering else "N/A",
                    "optimal_clusters": optimal_clusters,
                    "merged_clusters": 0,  # HDBSCAN不需要合并小聚类
                    "noise_points": noise_info["count"] if noise_info else 0
                }
            }
            
            # 添加噪声点信息（如果有）
            if noise_info:
                analysis_report["noise_info"] = noise_info
            
            # 打印详细的关键词信息，用于评估过滤效果
            print("=== 聚类关键词详情 ===")
            for cluster_id, keywords in cluster_keywords.items():
                print(f"聚类 {cluster_id}: {keywords}")
            
            app_logger.info("知识库数据聚类分析完成")
            return analysis_report
            
        except Exception as e:
            app_logger.error(f"聚类分析过程中出错：{str(e)}")
            return {"error": f"聚类分析过程中出错：{str(e)}"}
            
    except Exception as e:
        app_logger.error(f"初始化聚类分析时出错：{str(e)}")
        return {"error": f"初始化聚类分析时出错：{str(e)}"}


if __name__ == "__main__":
    # 测试知识库工具
    try:
        knowledge_base_tool = create_knowledge_base_tool()
        online_search_tool = create_online_search_tool()
        online_search_tool_v2 = create_online_search_tool_v2()
        
        # 从环境变量获取数据目录路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        text_path = os.path.join(script_dir, "data/test_input.txt")
        
        def test_online_search():
             # 测试在线搜索
            app_logger.info("测试在线搜索：")
            try:
                # 尝试运行搜索
                result = online_search_tool.invoke("历史上最大的国家是哪个")
                app_logger.info(f"搜索结果：{result}")
            except Exception as e:
                app_logger.error(f"搜索测试出错：{str(e)}")
                # 打印工具的描述信息，了解如何正确使用
            app_logger.info(f"工具描述：{online_search_tool.description}")
        
        def test_online_search_v2():
            # 测试在线搜索v2
            app_logger.info("测试在线搜索v2：")
            try:
                # 尝试运行搜索
                result = online_search_tool_v2.invoke("人工智能最新发展")
                app_logger.info(f"搜索结果：{result}")
            except Exception as e:
                app_logger.error(f"搜索测试出错：{str(e)}")
                # 打印工具的描述信息，了解如何正确使用
            app_logger.info(f"工具描述：{online_search_tool_v2.description}")
        
        def test_store_into_faiss():
            from sqlmodel import Session, select,create_engine
            from models.document import Document
            def get_db_engine():
                db_path = os.getenv("DATABASE_PATH")
                if not db_path:
                    raise ValueError("DATABASE_PATH environment variable is not set")
                return create_engine(
                    f"sqlite:///{db_path}",
                    pool_size=20,
                    max_overflow=30,
                    pool_timeout=60,
                    pool_recycle=3600,
                    pool_pre_ping=True,
                    echo=False
                )
            # 测试存储文档
            # 从 sqlite获取数据
            engine = get_db_engine()
            with Session(engine) as session:
                documents = session.exec(select(Document)).all()

                # 测试存储文档 - 直接传递Document对象列表
                app_logger.info(knowledge_base_tool.run({"action": "store", "documents": documents}))
            
        def test_retrieve_from_faiss():
            # 测试检索文档
            app_logger.info("测试检索文档：")
            app_logger.info(knowledge_base_tool.run({"action": "retrieve", "query": "外卖", "k": 3, "rerank": True}))

        def test_cluster_analysis():
            # 测试聚类分析
            app_logger.info("测试聚类分析：")
            app_logger.info(knowledge_base_tool.run({"action": "cluster_analysis"}))

        # test_cluster_analysis()
        # test_store_into_faiss()
        test_retrieve_from_faiss()
        # test_online_search()
    except Exception as e:
        app_logger.error(f"执行测试函数时出错：{str(e)}")
        print(f"错误：无法初始化知识库工具。错误信息：{str(e)}")
        print("请检查网络连接或尝试使用本地模型。")