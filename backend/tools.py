
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
from loguru import logger
from models.document import Document

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
                    "max_results": 3,  # 返回3个结果
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
                for result in results["results"]:
                    formatted_results.append({
                        "content": result.get("content", ""),
                        "url": result.get("url", ""),
                        "title": result.get("title", "")
                    })
                
                return formatted_results
            except requests.RequestException as e:
                return f"搜索请求出错：{str(e)}"
            except Exception as e:
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

# 知识库工具（向量数据库）
def create_knowledge_base_tool():
    """创建一个可以将数据存储在向量数据库并进行检索的工具"""
    # 从环境变量获取模型名称
    embedding_model_name = os.getenv("EMBEDDING_MODEL_NAME")
    rerank_model_name = os.getenv("RERANK_MODEL_NAME")
    
    # 初始化嵌入模型
    # 注意：当前版本的langchain_huggingface可能会显示FutureWarning: `resume_download` is deprecated
    # 这是一个警告，不影响功能正常运行
    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model_name,
        model_kwargs={'device': 'cpu'}
    )
    
    # 初始化重排模型 - 使用公开可用的模型
    try:
        reranker = CrossEncoder(rerank_model_name, device='cpu')
    except Exception as e:
        print(f"警告：无法加载重排模型 {rerank_model_name}，错误：{str(e)}")
        print("将使用简单相似度检索，不进行重排")
        # 设置一个标志，表示重排模型不可用
        reranker = None
    
    # 初始化向量数据库
    # 如果向量数据库文件不存在，则创建新的
    # 从环境变量获取路径，数据存储在backend/data目录下
    faiss_index_path = os.getenv("FAISS_INDEX_PATH")
    
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
            print(f"警告：加载向量数据库失败，将创建新的数据库。错误：{str(e)}")
            # 创建新的向量数据库
            vectorstore = FAISS.from_texts(["Placeholder text"], embeddings)
            vectorstore.save_local(vectorstore_path)
    else:
        # 创建空的向量数据库
        vectorstore = FAISS.from_texts(["Placeholder text"], embeddings)
        vectorstore.save_local(vectorstore_path)
    
    # 文档处理函数
    def process_and_store_documents(documents: list[Document]):
        """处理文档并存储到向量数据库"""
        # 分割文档
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        # 分割所有文档并添加元数据
        all_chunks = []
        all_metadatas = []
        for i, doc in enumerate(documents):
            # 从Document对象中提取内容
            content = doc.content if hasattr(doc, 'content') else str(doc)
            chunks = text_splitter.split_text(content)
            # 为每个文档片段添加元数据
            metadatas = [{"source": f"document_{i}", "chunk": j, "title": doc.title if hasattr(doc, 'title') else f"Document_{i}"} for j in range(len(chunks))]
            all_chunks.extend(chunks)
            all_metadatas.extend(metadatas)
        
        # 添加到向量数据库（包含元数据）
        vectorstore.add_texts(all_chunks, all_metadatas)
        
        # 保存向量数据库到环境变量指定的路径
        vectorstore.save_local(vectorstore_path)
        
        return f"成功处理并存储了{len(all_chunks)}个文档片段到向量数据库"
    
    # 检索函数
    def retrieve_from_knowledge_base(query, k=3, rerank=True):
        """从向量数据库中检索最相关的文档"""
        # 获取初始检索结果
        if rerank and reranker is not None:
            # 为了重排需要获取更多结果
            initial_k = k * 3
        else:
            initial_k = k
            # 如果没有重排模型或不进行重排，则不进行额外处理
            rerank = False
            
        results = vectorstore.similarity_search(query, k=initial_k)
        
        # 使用重排模型对结果进行排序（仅在模型可用时）
        if rerank and results and reranker is not None:
            try:
                # 准备用于重排的文本对
                sentence_pairs = [[query, result.page_content] for result in results]
                # 获取重排分数
                scores = reranker.predict(sentence_pairs)
                
                # 按分数降序排序
                results_with_scores = list(zip(results, scores))
                results_with_scores.sort(key=lambda x: x[1], reverse=True)
                
                # 只保留前k个结果
                results = [result for result, _ in results_with_scores[:k]]
            except Exception as e:
                print(f"警告：重排过程出错，将使用原始检索结果。错误：{str(e)}")
        
        # 格式化结果
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append({
                "id": i,
                "content": result.page_content,
                "metadata": result.metadata
            })
        
        return formatted_results
    
    # 创建工具 - 进一步调整函数实现以处理不同的数据类型
    def knowledge_base_func(action: str, documents: list[dict] = None, query=None, k: int = 3, rerank: bool = True):
        """处理知识库工具的输入数据
        
        Args:
            action: 操作类型，支持'store'和'retrieve'
            documents: 对于'store'操作，是文档字典列表，每个字典应包含'title'和'content'字段
            query: 对于'retrieve'操作，是查询字符串
            k: 对于'retrieve'操作，返回结果数量，默认为3
            rerank: 对于'retrieve'操作，是否启用结果重排，默认为True
        """
        if action == "store":
            # 将字典列表转换为Document对象列表
            document_objects = []
            for doc_dict in documents:
                doc = Document(
                    title=doc_dict.get("title", "Untitled"),
                    content=doc_dict.get("content", ""),
                    source=doc_dict.get("source", "unknown"),
                    url=doc_dict.get("url", "")
                )
                document_objects.append(doc)
            return process_and_store_documents(document_objects)
        elif action == "retrieve":
            return retrieve_from_knowledge_base(query, k, rerank)
        else:
            return f"不支持的操作：{action}"
    
    knowledge_base_tool = StructuredTool.from_function(
        func=knowledge_base_func,
        name="KnowledgeBase",
        description="用于处理和检索向量数据库中的知识，支持存储文档(store)和检索信息(retrieve)两种操作"
    )
    
    return knowledge_base_tool

if __name__ == "__main__":
    # 测试知识库工具
    knowledge_base_tool = create_knowledge_base_tool()
    online_search_tool = create_online_search_tool()
    
    # 从环境变量获取数据目录路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    text_path = os.path.join(script_dir, "data/test_input.txt")
    
    with open(text_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # 创建文档字典
        test_doc = {
            "title": "倒悬的第七次日落",
            "content": content,
            "source": "test_input.txt",
            "url": "local://test_input.txt"
        }
        # 测试存储文档
        print(knowledge_base_tool.run({"action": "store", "documents": [test_doc]}))
        
        
    # 测试检索文档
    print("测试检索文档：")
    print(knowledge_base_tool.run({"action": "retrieve", "query": "倒悬的第七次日落", "k": 3, "rerank": True}))

    # # 测试在线搜索
    # print("测试在线搜索：")
    # try:
    #     # 尝试运行搜索
    #     result = online_search_tool.invoke("历史上最大的国家是哪个")
    #     print(f"搜索结果：{result}")
    # except Exception as e:
    #     print(f"搜索测试出错：{str(e)}")
    #     # 打印工具的描述信息，了解如何正确使用
    #     print(f"工具描述：{online_search_tool.description}")