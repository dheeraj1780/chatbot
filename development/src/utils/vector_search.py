from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List, Dict, Optional
import os

class VectorSearchService:
    def __init__(self, chroma_path: str = "chroma_db"):
        self.chroma_path = chroma_path
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vector_db = self._initialize_vector_db()
    
    def _initialize_vector_db(self):
        """Initialize or load existing vector database"""
        if os.path.exists(self.chroma_path):
            return Chroma(
                persist_directory=self.chroma_path,
                embedding_function=self.embeddings
            )
        else:
            return Chroma(
                persist_directory=self.chroma_path,
                embedding_function=self.embeddings
            )
    
    async def search_with_group_filter(self, query: str, group_id: int, k: int = 5) -> List[Dict]:
        """Search within a specific group"""
        try:
            filter_dict = {"group_id": group_id}
            
            docs_with_scores = self.vector_db.similarity_search_with_score(
                query, 
                k=k, 
                filter=filter_dict
            )
            
            results = []
            for doc, score in docs_with_scores:
                results.append({
                    "content": doc.page_content,
                    "score": float(score),
                    "metadata": doc.metadata
                })
            
            return results
            
        except Exception as e:
            raise Exception(f"Error in group-filtered search: {str(e)}")
    
    async def search_all_documents(self, query: str, k: int = 5) -> List[Dict]:
        """Search across all documents"""
        try:
            docs_with_scores = self.vector_db.similarity_search_with_score(query, k=k)
            
            results = []
            for doc, score in docs_with_scores:
                results.append({
                    "content": doc.page_content,
                    "score": float(score),
                    "metadata": doc.metadata
                })
            
            return results
            
        except Exception as e:
            raise Exception(f"Error in global search: {str(e)}")
    
    def add_documents_to_vector_db(self, chunks_with_metadata):
        """Add document chunks to vector database"""
        try:
            self.vector_db.add_documents(chunks_with_metadata)
            return len(chunks_with_metadata)
        except Exception as e:
            raise Exception(f"Error adding documents to vector DB: {str(e)}")
    
    def delete_documents_by_filter(self, filter_dict: Dict):
        """Delete documents from vector DB by filter"""
        try:
            # Note: Chroma doesn't have direct delete by filter
            # You might need to implement custom logic or use document IDs
            pass
        except Exception as e:
            raise Exception(f"Error deleting documents: {str(e)}")