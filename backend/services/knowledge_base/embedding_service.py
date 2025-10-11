"""
Embedding service for text vectorization.
"""
import os
import warnings
from typing import List, Optional
from langchain_huggingface import HuggingFaceEmbeddings
from utils.logging_config import app_logger
from config.settings import settings

# Suppress huggingface_hub warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="huggingface_hub")


class EmbeddingService:
    """Service for text embedding operations."""
    
    def __init__(self):
        self.embeddings = None
        self.model_name = settings.EMBEDDING_MODEL_NAME
        self._initialize_embeddings()
    
    def _initialize_embeddings(self):
        """Initialize embedding model."""
        # List of fallback models
        embedding_models = [
            self.model_name,
            "sentence-transformers/all-MiniLM-L6-v2",
            "paraphrase-multilingual-MiniLM-L12-v2", 
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            "sentence-transformers/distiluse-base-multilingual-cased"
        ]
        
        for model_name in embedding_models:
            try:
                app_logger.info(f"Trying to load embedding model: {model_name}")
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=model_name,
                    model_kwargs={'device': 'cpu'},
                    cache_folder="./models_cache"
                )
                self.model_name = model_name
                app_logger.info(f"Successfully loaded embedding model: {model_name}")
                break
            except Exception as e:
                app_logger.warning(f"Failed to load embedding model {model_name}: {str(e)}")
                continue
        
        if self.embeddings is None:
            app_logger.error("All embedding models failed to load")
            raise Exception("Unable to load any embedding model")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            app_logger.info(f"Embedding {len(texts)} texts using model: {self.model_name}")
            embeddings = self.embeddings.embed_documents(texts)
            app_logger.info(f"Successfully embedded {len(embeddings)} texts")
            return embeddings
        except Exception as e:
            app_logger.error(f"Error embedding texts: {str(e)}")
            raise
    
    def embed_query(self, query: str) -> List[float]:
        """
        Embed a single query string.
        
        Args:
            query: Query string to embed
            
        Returns:
            Embedding vector
        """
        try:
            app_logger.info(f"Embedding query: '{query[:50]}...'")
            embedding = self.embeddings.embed_query(query)
            app_logger.info("Query embedding successful")
            return embedding
        except Exception as e:
            app_logger.error(f"Error embedding query: {str(e)}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors."""
        try:
            # Test with a simple query to get dimension
            test_embedding = self.embed_query("test")
            return len(test_embedding)
        except Exception as e:
            app_logger.error(f"Error getting embedding dimension: {str(e)}")
            return 384  # Default dimension for most models
    
    def is_available(self) -> bool:
        """Check if embedding service is available."""
        return self.embeddings is not None


# Global service instance
embedding_service = EmbeddingService()
