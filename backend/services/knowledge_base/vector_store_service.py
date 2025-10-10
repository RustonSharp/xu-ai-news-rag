"""
Vector store service for FAISS operations.
"""
import os
from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from services.knowledge_base.embedding_service import embedding_service
from services.knowledge_base.rerank_service import rerank_service
from utils.logging_config import app_logger
from config.settings import settings


class VectorStoreService:
    """Service for vector store operations using FAISS."""
    
    def __init__(self):
        self.vectorstore = None
        self.index_path = settings.FAISS_INDEX_PATH
        self.vectorstore_path = os.path.dirname(self.index_path)
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Initialize or load FAISS vector store."""
        try:
            # Ensure directory exists
            if not os.path.exists(self.vectorstore_path):
                os.makedirs(self.vectorstore_path)
            
            # Try to load existing vectorstore
            if os.path.exists(self.index_path):
                try:
                    self.vectorstore = FAISS.load_local(
                        self.vectorstore_path, 
                        embedding_service.embeddings, 
                        allow_dangerous_deserialization=True
                    )
                    app_logger.info("Successfully loaded existing vector store")
                except Exception as e:
                    app_logger.warning(f"Failed to load existing vector store: {str(e)}")
                    self._create_new_vectorstore()
            else:
                self._create_new_vectorstore()
                
        except Exception as e:
            app_logger.error(f"Error initializing vector store: {str(e)}")
            raise
    
    def _create_new_vectorstore(self):
        """Create a new vector store with placeholder text."""
        try:
            app_logger.info("Creating new vector store")
            self.vectorstore = FAISS.from_texts(
                ["Placeholder text"], 
                embedding_service.embeddings
            )
            self.save_vectorstore()
            app_logger.info("New vector store created successfully")
        except Exception as e:
            app_logger.error(f"Error creating new vector store: {str(e)}")
            raise
    
    def save_vectorstore(self):
        """Save vector store to disk."""
        try:
            self.vectorstore.save_local(self.vectorstore_path)
            app_logger.info(f"Vector store saved to: {self.vectorstore_path}")
        except Exception as e:
            app_logger.error(f"Error saving vector store: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> str:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            Success message
        """
        try:
            app_logger.info(f"Adding {len(documents)} documents to vector store")
            
            # Process documents
            all_chunks, all_metadatas = self._process_documents(documents)
            
            # Check if vectorstore has only placeholder text
            if self._has_only_placeholder():
                app_logger.info("Replacing placeholder vector store with new documents")
                self._replace_placeholder_vectorstore(all_chunks, all_metadatas)
            else:
                app_logger.info("Adding documents to existing vector store")
                self.vectorstore.add_texts(all_chunks, all_metadatas)
            
            # Save the updated vectorstore
            self.save_vectorstore()
            
            message = f"Successfully processed and stored {len(all_chunks)} document chunks"
            app_logger.info(f"Document storage completed: {message}")
            return message
            
        except Exception as e:
            app_logger.error(f"Error adding documents to vector store: {str(e)}")
            raise
    
    def _process_documents(self, documents: List[Dict[str, Any]]) -> tuple[List[str], List[Dict[str, Any]]]:
        """Process documents into chunks with metadata."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        all_chunks = []
        all_metadatas = []
        
        for i, doc in enumerate(documents):
            # Extract content and metadata
            content = doc.get("description", "")
            title = doc.get("title", f"Document_{i}")
            tags = doc.get("tags", "")
            pub_date = doc.get("pub_date", "")
            author = doc.get("author", "")
            
            # Split content into chunks
            chunks = text_splitter.split_text(content)
            
            # Create metadata for each chunk
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
        
        return all_chunks, all_metadatas
    
    def _has_only_placeholder(self) -> bool:
        """Check if vectorstore contains only placeholder text."""
        try:
            if len(self.vectorstore.index_to_docstore_id) == 1:
                first_doc_id = list(self.vectorstore.index_to_docstore_id.values())[0]
                first_doc = self.vectorstore.docstore.search(first_doc_id)
                return "Placeholder text" in str(first_doc)
            return False
        except Exception:
            return False
    
    def _replace_placeholder_vectorstore(self, chunks: List[str], metadatas: List[Dict[str, Any]]):
        """Replace placeholder vectorstore with new documents."""
        new_vectorstore = FAISS.from_texts(chunks, embedding_service.embeddings, metadatas=metadatas)
        self.vectorstore.index_to_docstore_id = new_vectorstore.index_to_docstore_id
        self.vectorstore.docstore = new_vectorstore.docstore
        self.vectorstore.index = new_vectorstore.index
    
    def search(self, query: str, k: int = 3, rerank: bool = True) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            k: Number of results to return
            rerank: Whether to use reranking
            
        Returns:
            List of search results
        """
        try:
            app_logger.info(f"Searching vector store for: '{query}'")
            
            # Determine initial search count
            initial_k = k * 3 if rerank and rerank_service.is_available() else k
            
            # Perform similarity search
            results = self.vectorstore.similarity_search(query, k=initial_k)
            app_logger.info(f"Found {len(results)} initial results")
            
            # Apply reranking if requested and available
            if rerank and rerank_service.is_available() and results:
                results = rerank_service.rerank_results(query, results, k)
                app_logger.info(f"Reranked to top {len(results)} results")
            
            # Format results
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append({
                    "id": i,
                    "content": result.page_content,
                    "metadata": result.metadata
                })
            
            app_logger.info(f"Vector store search completed, returning {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            app_logger.error(f"Error searching vector store: {str(e)}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        try:
            total_docs = len(self.vectorstore.index_to_docstore_id)
            return {
                "total_documents": total_docs,
                "index_path": self.index_path,
                "embedding_model": embedding_service.model_name,
                "rerank_available": rerank_service.is_available()
            }
        except Exception as e:
            app_logger.error(f"Error getting vector store stats: {str(e)}")
            return {"error": str(e)}
    
    def create_search_tool(self):
        """Create a search tool for the vector store."""
        from langchain_core.tools import StructuredTool
        
        def search_func(query: str, k: int = 3, rerank: bool = True) -> List[Dict[str, Any]]:
            """Search the vector store for relevant documents."""
            try:
                results = self.retrieve_with_rerank(query, k, rerank)
                return results
            except Exception as e:
                app_logger.error(f"Error in search tool: {str(e)}")
                return []
        
        return StructuredTool.from_function(
            func=search_func,
            name="vector_search",
            description="Search the vector store for relevant documents"
        )


# Global service instance
vector_store_service = VectorStoreService()
