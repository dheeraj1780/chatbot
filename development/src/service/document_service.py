from fastapi import UploadFile
import os
from typing import List
from repository.orm import DocumentRepository, GroupRepository
from utils.db_connection import get_db_session
from utils.document_processor import DocumentProcessor
import tempfile

class DocumentService:
    def __init__(self):
        self.document_processor = DocumentProcessor()

    async def create_document_group(self, name: str, description: str):
        """Create a new document group"""
        async with get_db_session() as session:
            group_repo = GroupRepository(session)
            group = await group_repo.create_group(name, description)
            return {
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "created_at": group.created_at.isoformat()
            }

    async def get_all_groups(self):
        """Get all document groups"""
        async with get_db_session() as session:
            group_repo = GroupRepository(session)
            groups = await group_repo.get_all_groups()
            return [
                {
                    "id": group.id,
                    "name": group.name,
                    "description": group.description,
                    "created_at": group.created_at.isoformat()
                }
                for group in groups
            ]

    async def upload_and_process_document(self, file: UploadFile, group_id: int):
        """Upload and process a document"""
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise ValueError("Only PDF files are supported")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        try:
            async with get_db_session() as session:
                doc_repo = DocumentRepository(session)
                
                # Save document metadata
                document = await doc_repo.create_document(
                    filename=file.filename,
                    file_path=temp_path,
                    group_id=group_id
                )
                
                # Process document and create embeddings
                chunks_created = await self.document_processor.process_document(
                    temp_path, document.id, group_id
                )
                
                return {
                    "document_id": document.id,
                    "filename": document.filename,
                    "group_id": group_id,
                    "chunks_created": chunks_created,
                    "message": "Document uploaded and processed successfully"
                }
        finally:
            # Clean up temporary file
            os.unlink(temp_path)

    async def get_documents_by_group(self, group_id: int):
        """Get all documents in a specific group"""
        async with get_db_session() as session:
            doc_repo = DocumentRepository(session)
            documents = await doc_repo.get_documents_by_group(group_id)
            return [
                {
                    "id": doc.id,
                    "filename": doc.filename,
                    "group_id": doc.group_id,
                    "group_name": doc.group.name,
                    "uploaded_at": doc.uploaded_at.isoformat()
                }
                for doc in documents
            ]

    async def delete_document(self, document_id: int):
        """Delete a document and its vector embeddings"""
        async with get_db_session() as session:
            doc_repo = DocumentRepository(session)
            
            # Get document info
            document = await doc_repo.get_document_by_id(document_id)
            if not document:
                raise ValueError("Document not found")
            
            # Delete from vector database
            await self.document_processor.delete_document_chunks(document_id)
            
            # Delete from PostgreSQL
            await doc_repo.delete_document(document_id)
