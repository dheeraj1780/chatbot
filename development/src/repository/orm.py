from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from repository.schema.schema import User, DocumentGroup, Document, ChunkMetadata
from typing import List, Optional

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def create_user(self, username: str, password_hash: str, role: str = "user") -> User:
        """Create a new user"""
        user = User(username=username, password_hash=password_hash, role=role)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

class GroupRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_group(self, name: str, description: str) -> DocumentGroup:
        """Create a new document group"""
        group = DocumentGroup(name=name, description=description)
        self.session.add(group)
        await self.session.commit()
        await self.session.refresh(group)
        return group

    async def get_all_groups(self) -> List[DocumentGroup]:
        """Get all document groups"""
        result = await self.session.execute(select(DocumentGroup))
        return result.scalars().all()

    async def get_group_by_id(self, group_id: int) -> Optional[DocumentGroup]:
        """Get group by ID"""
        result = await self.session.execute(
            select(DocumentGroup).where(DocumentGroup.id == group_id)
        )
        return result.scalar_one_or_none()

class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_document(self, filename: str, file_path: str, group_id: int) -> Document:
        """Create a new document"""
        document = Document(filename=filename, file_path=file_path, group_id=group_id)
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        return document

    async def get_documents_by_group(self, group_id: int) -> List[Document]:
        """Get all documents in a group"""
        result = await self.session.execute(
            select(Document)
            .options(selectinload(Document.group))
            .where(Document.group_id == group_id)
        )
        return result.scalars().all()

    async def get_document_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID"""
        result = await self.session.execute(
            select(Document).where(Document.id == document_id)
        )
        return result.scalar_one_or_none()

    async def delete_document(self, document_id: int):
        """Delete a document and its metadata"""
        # Delete chunk metadata
        await self.session.execute(
            delete(ChunkMetadata).where(ChunkMetadata.document_id == document_id)
        )
        
        # Delete document
        await self.session.execute(
            delete(Document).where(Document.id == document_id)
        )
        
        await self.session.commit()

class ChunkMetadataRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_chunk_metadata(self, chunk_id: str, document_id: int, 
                                  group_id: int, chunk_index: int) -> ChunkMetadata:
        """Create chunk metadata"""
        metadata = ChunkMetadata(
            chunk_id=chunk_id,
            document_id=document_id,
            group_id=group_id,
            chunk_index=chunk_index
        )
        self.session.add(metadata)
        await self.session.commit()
        await self.session.refresh(metadata)
        return metadata