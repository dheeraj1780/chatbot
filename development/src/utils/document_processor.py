from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.vector_search import VectorSearchService
from utils.db_connection import get_db_session
from repository.orm import ChunkMetadataRepository
from typing import List
import asyncio

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
        )
        self.vector_service = VectorSearchService()
    
    async def process_document(self, file_path: str, document_id: int, group_id: int) -> int:
        """Process a document and create embeddings"""
        try:
            # Load document
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            
            # Split into chunks
            chunks = self.text_splitter.split_documents(pages)
            
            # Add metadata to chunks
            chunks_with_metadata = []
            async with get_db_session() as session:
                chunk_repo = ChunkMetadataRepository(session)
                
                for i, chunk in enumerate(chunks):
                    chunk_id = f"doc_{document_id}_chunk_{i}"
                    
                    # Update chunk metadata
                    chunk.metadata.update({
                        'chunk_id': chunk_id,
                        'document_id': document_id,
                        'group_id': group_id,
                        'chunk_index': i
                    })
                    
                    chunks_with_metadata.append(chunk)
                    
                    # Store metadata in PostgreSQL
                    await chunk_repo.create_chunk_metadata(
                        chunk_id=chunk_id,
                        document_id=document_id,
                        group_id=group_id,
                        chunk_index=i
                    )
            
            # Add to vector database
            chunks_created = self.vector_service.add_documents_to_vector_db(chunks_with_metadata)
            
            return chunks_created
            
        except Exception as e:
            raise Exception(f"Error processing document: {str(e)}")
    
    async def delete_document_chunks(self, document_id: int):
        """Delete all chunks for a specific document"""
        try:
            # This is a simplified version - you might need to implement
            # more sophisticated deletion logic based on your vector DB capabilities
            filter_dict = {"document_id": document_id}
            self.vector_service.delete_documents_by_filter(filter_dict)
        except Exception as e:
            raise Exception(f"Error deleting document chunks: {str(e)}")
