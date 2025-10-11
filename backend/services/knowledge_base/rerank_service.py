"""
Reranking service for search result optimization.
"""
import warnings
from typing import List, Tuple, Optional
from sentence_transformers import CrossEncoder
from utils.logging_config import app_logger
from config.settings import settings

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)


class RerankService:
    """Service for reranking search results."""
    
    def __init__(self):
        self.reranker = None
        self.model_name = settings.RERANK_MODEL_NAME
        self._initialize_reranker()
    
    def _initialize_reranker(self):
        """Initialize reranking model."""
        try:
            app_logger.info(f"Initializing reranker with model: {self.model_name}")
            self.reranker = CrossEncoder(self.model_name, device='cpu')
            app_logger.info("Reranker initialized successfully")
        except Exception as e:
            app_logger.warning(f"Failed to initialize reranker {self.model_name}: {str(e)}")
            app_logger.info("Will use simple similarity retrieval without reranking")
            self.reranker = None
    
    def rerank_results(self, query: str, results: List[dict], top_k: int = 3) -> List[dict]:
        """
        Rerank search results based on query relevance.
        
        Args:
            query: Search query
            results: List of search results
            top_k: Number of top results to return
            
        Returns:
            Reranked list of results
        """
        if not self.reranker or not results:
            app_logger.info("Skipping reranking - no reranker or no results")
            return results[:top_k]
        
        try:
            app_logger.info(f"Reranking {len(results)} results for query: '{query[:50]}...'")
            
            # Prepare sentence pairs for reranking
            sentence_pairs = [[query, result.get("content", "")] for result in results]
            
            # Get reranking scores
            scores = self.reranker.predict(sentence_pairs)
            app_logger.info(f"Reranking scores calculated: {scores}")
            
            # Combine results with scores and sort
            results_with_scores = list(zip(results, scores))
            results_with_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Return top-k results
            reranked_results = [result for result, _ in results_with_scores[:top_k]]
            app_logger.info(f"Reranking completed, returning top {len(reranked_results)} results")
            
            return reranked_results
            
        except Exception as e:
            app_logger.warning(f"Reranking failed: {str(e)}, using original results")
            return results[:top_k]
    
    def is_available(self) -> bool:
        """Check if reranking service is available."""
        return self.reranker is not None
    
    def get_model_name(self) -> str:
        """Get the name of the reranking model."""
        return self.model_name if self.reranker else "none"


# Global service instance
rerank_service = RerankService()
