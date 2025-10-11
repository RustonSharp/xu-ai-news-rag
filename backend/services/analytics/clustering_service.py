"""
Clustering service for document analysis.
"""
import os
import json
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
from collections import Counter
from services.knowledge_base.vector_store_service import vector_store_service
from services.analytics.text_processing import text_processing_service
from utils.logging_config import app_logger

# Try to import advanced clustering libraries
try:
    import umap
    import hdbscan
    ADVANCED_CLUSTERING_AVAILABLE = True
except ImportError:
    ADVANCED_CLUSTERING_AVAILABLE = False
    app_logger.warning("Advanced clustering libraries (UMAP, HDBSCAN) not available, using K-means")


class ClusteringService:
    """Service for document clustering analysis."""
    
    def __init__(self):
        self.vectorizer = None
        self._initialize_vectorizer()
    
    def _initialize_vectorizer(self):
        """Initialize TF-IDF vectorizer."""
        self.vectorizer = TfidfVectorizer(
            max_features=2000,
            stop_words=text_processing_service.custom_stop_words,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8,
            sublinear_tf=True
        )
    
    def perform_clustering_analysis(self) -> Dict[str, Any]:
        """
        Perform comprehensive clustering analysis on the knowledge base.
        
        Returns:
            Clustering analysis results
        """
        try:
            app_logger.info("Starting clustering analysis")
            
            # Get all documents from vector store
            documents = self._extract_documents_from_vectorstore()
            if len(documents) < 10:
                app_logger.warning("Insufficient documents for clustering analysis")
                return {"error": "Insufficient documents for clustering analysis"}
            
            # Preprocess documents
            processed_contents = self._preprocess_documents(documents)
            
            # Perform clustering
            cluster_labels, optimal_clusters, silhouette_avg = self._perform_clustering(processed_contents)
            
            # Extract cluster information
            cluster_info = self._extract_cluster_info(documents, cluster_labels, processed_contents)
            
            # Generate analysis report
            analysis_report = {
                "total_documents": len(documents),
                "total_clusters": optimal_clusters,
                "analysis_date": str(np.datetime64('now')),
                "top_clusters": cluster_info[:10],  # Top 10 clusters
                "cluster_distribution": self._get_cluster_distribution(cluster_labels),
                "silhouette_score": silhouette_avg,
                "clustering_method": "HDBSCAN with UMAP" if ADVANCED_CLUSTERING_AVAILABLE else "K-means",
                "optimization_info": {
                    "original_clusters": optimal_clusters,
                    "optimal_clusters": optimal_clusters,
                    "merged_clusters": 0,
                    "noise_points": sum(1 for label in cluster_labels if label == -1) if ADVANCED_CLUSTERING_AVAILABLE else 0
                }
            }
            
            app_logger.info("Clustering analysis completed successfully")
            return analysis_report
            
        except Exception as e:
            app_logger.error(f"Error in clustering analysis: {str(e)}")
            return {"error": f"Clustering analysis failed: {str(e)}"}
    
    def _extract_documents_from_vectorstore(self) -> List[Dict[str, Any]]:
        """Extract all documents from the vector store."""
        try:
            # This is a simplified approach - in practice, you might want to store
            # document metadata separately for easier access
            documents = []
            
            # Get all document IDs from vector store
            docstore = vector_store_service.vectorstore.docstore
            index_to_docstore_id = vector_store_service.vectorstore.index_to_docstore_id
            
            for idx, doc_id in enumerate(index_to_docstore_id.values()):
                try:
                    doc = docstore.search(doc_id)
                    if doc is not None:
                        if hasattr(doc, 'page_content'):
                            documents.append({
                                "content": doc.page_content,
                                "metadata": doc.metadata if hasattr(doc, 'metadata') else {}
                            })
                        else:
                            documents.append({
                                "content": str(doc),
                                "metadata": {}
                            })
                except (KeyError, AttributeError):
                    continue
            
            app_logger.info(f"Extracted {len(documents)} documents from vector store")
            return documents
            
        except Exception as e:
            app_logger.error(f"Error extracting documents from vector store: {str(e)}")
            return []
    
    def _preprocess_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Preprocess documents for clustering."""
        processed_contents = []
        
        for doc in documents:
            tags = doc.get("metadata", {}).get("tags", "")
            processed_content = text_processing_service.preprocess_text(doc["content"], tags)
            processed_contents.append(processed_content)
        
        return processed_contents
    
    def _perform_clustering(self, processed_contents: List[str]) -> Tuple[List[int], int, float]:
        """Perform clustering using available methods."""
        # Create TF-IDF matrix
        tfidf_matrix = self.vectorizer.fit_transform(processed_contents)
        
        if ADVANCED_CLUSTERING_AVAILABLE and len(processed_contents) > 10:
            return self._perform_advanced_clustering(tfidf_matrix, processed_contents)
        else:
            return self._perform_kmeans_clustering(tfidf_matrix)
    
    def _perform_advanced_clustering(self, tfidf_matrix, processed_contents: List[str]) -> Tuple[List[int], int, float]:
        """Perform advanced clustering using UMAP + HDBSCAN."""
        try:
            # UMAP dimensionality reduction
            n_neighbors = min(15, max(5, int(len(processed_contents) * 0.3)))
            n_components = min(50, len(processed_contents) - 1, len(processed_contents) // 2)
            
            if n_components < 2:
                n_components = 2
            
            reducer = umap.UMAP(
                n_components=n_components,
                n_neighbors=n_neighbors,
                min_dist=0.05,
                metric='cosine',
                random_state=42
            )
            
            if len(processed_contents) <= 10:
                embedding = tfidf_matrix.toarray()
            else:
                embedding = reducer.fit_transform(tfidf_matrix)
                # Standardize the embedding
                from sklearn.preprocessing import StandardScaler
                scaler = StandardScaler()
                embedding = scaler.fit_transform(embedding)
            
            # HDBSCAN clustering
            min_cluster_size = max(2, int(len(processed_contents) * 0.03))
            min_samples = max(1, int(len(processed_contents) * 0.01))
            
            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=min_cluster_size,
                min_samples=min_samples,
                metric='euclidean',
                cluster_selection_method='eom'
            )
            
            cluster_labels = clusterer.fit_predict(embedding)
            
            # Calculate silhouette score
            unique_labels = set(cluster_labels)
            if -1 in unique_labels:
                unique_labels.remove(-1)
            
            optimal_clusters = len(unique_labels)
            silhouette_avg = 0.0
            
            if optimal_clusters > 1:
                non_noise_indices = [i for i, label in enumerate(cluster_labels) if label != -1]
                if len(non_noise_indices) > optimal_clusters:
                    silhouette_avg = silhouette_score(
                        embedding[non_noise_indices], 
                        cluster_labels[non_noise_indices]
                    )
            
            app_logger.info(f"HDBSCAN clustering completed: {optimal_clusters} clusters, silhouette: {silhouette_avg:.4f}")
            return cluster_labels, optimal_clusters, silhouette_avg
            
        except Exception as e:
            app_logger.warning(f"Advanced clustering failed: {str(e)}, falling back to K-means")
            return self._perform_kmeans_clustering(tfidf_matrix)
    
    def _perform_kmeans_clustering(self, tfidf_matrix) -> Tuple[List[int], int, float]:
        """Perform K-means clustering."""
        max_possible_clusters = min(15, len(tfidf_matrix) // 2) if len(tfidf_matrix) > 20 else 10
        if max_possible_clusters < 2:
            max_possible_clusters = 2
        
        # Find optimal number of clusters
        silhouette_scores = []
        possible_clusters = range(2, min(max_possible_clusters + 1, 11))
        
        for n_clusters in possible_clusters:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(tfidf_matrix)
            silhouette_avg = silhouette_score(tfidf_matrix, cluster_labels)
            silhouette_scores.append(silhouette_avg)
        
        # Choose best number of clusters
        optimal_clusters = possible_clusters[silhouette_scores.index(max(silhouette_scores))]
        silhouette_avg = max(silhouette_scores)
        
        # Final clustering
        kmeans = KMeans(n_clusters=optimal_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(tfidf_matrix)
        
        app_logger.info(f"K-means clustering completed: {optimal_clusters} clusters, silhouette: {silhouette_avg:.4f}")
        return cluster_labels, optimal_clusters, silhouette_avg
    
    def _extract_cluster_info(self, documents: List[Dict[str, Any]], cluster_labels: List[int], processed_contents: List[str]) -> List[Dict[str, Any]]:
        """Extract information for each cluster."""
        # Get feature names
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Group documents by cluster
        cluster_docs = {}
        for i, label in enumerate(cluster_labels):
            if label not in cluster_docs:
                cluster_docs[label] = []
            cluster_docs[label].append({
                "index": i,
                "content": documents[i]["content"],
                "metadata": documents[i]["metadata"]
            })
        
        # Calculate cluster statistics
        cluster_info = []
        for cluster_id, docs in cluster_docs.items():
            if cluster_id == -1:  # Skip noise points
                continue
            
            # Calculate cluster size and percentage
            cluster_size = len(docs)
            percentage = (cluster_size / len(documents)) * 100
            
            # Extract keywords for this cluster
            keywords = self._extract_cluster_keywords(docs, feature_names)
            
            # Generate cluster label
            cluster_label = text_processing_service.generate_cluster_label(keywords)
            
            # Get sample documents
            sample_docs = docs[:3]  # First 3 documents as samples
            
            cluster_info.append({
                "cluster_id": int(cluster_id),
                "cluster_label": cluster_label,
                "document_count": cluster_size,
                "percentage": round(percentage, 2),
                "keywords": keywords[:10],  # Top 10 keywords
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
                    for doc in sample_docs
                ]
            })
        
        # Sort by document count
        cluster_info.sort(key=lambda x: x["document_count"], reverse=True)
        return cluster_info
    
    def _extract_cluster_keywords(self, cluster_docs: List[Dict[str, Any]], feature_names: List[str]) -> List[str]:
        """Extract keywords for a specific cluster."""
        # Combine all documents in the cluster
        cluster_text = ' '.join([doc["content"] for doc in cluster_docs])
        
        # Extract keywords using text processing service
        keywords = text_processing_service.extract_keywords(cluster_text, max_keywords=10)
        
        return keywords
    
    def _get_cluster_distribution(self, cluster_labels: List[int]) -> Dict[str, int]:
        """Get distribution of documents across clusters."""
        distribution = Counter(cluster_labels)
        return {str(cluster_id): count for cluster_id, count in distribution.items()}


# Global service instance
clustering_service = ClusteringService()
