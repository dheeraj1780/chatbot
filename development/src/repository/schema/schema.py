# ===== repository/schema/schema.py =====
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")  # admin, user
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"

class DocumentGroup(Base):
    __tablename__ = "document_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    documents = relationship("Document", back_populates="group", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DocumentGroup(name='{self.name}')>"

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    group_id = Column(Integer, ForeignKey("document_groups.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    group = relationship("DocumentGroup", back_populates="documents")
    chunk_metadata = relationship("ChunkMetadata", back_populates="document", cascade="all, delete-orphan")
    
    # Index for faster queries
    __table_args__ = (Index('idx_document_group', 'group_id'),)
    
    def __repr__(self):
        return f"<Document(filename='{self.filename}', group_id={self.group_id})>"

class ChunkMetadata(Base):
    __tablename__ = "chunks_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(String(100), unique=True, nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("document_groups.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="chunk_metadata")
    group = relationship("DocumentGroup")
    
    # Composite index for faster filtering
    __table_args__ = (
        Index('idx_chunk_group_doc', 'group_id', 'document_id'),
        Index('idx_chunk_group', 'group_id'),
    )
    
    def __repr__(self):
        return f"<ChunkMetadata(chunk_id='{self.chunk_id}', group_id={self.group_id})>"


# ===== utils/db_connection.py =====


# ===== utils/slm_call.py =====


# ===== utils/vector_search.py =====


# ===== utils/document_processor.py =====


# ===== requirements.txt =====



# ===== docker-compose.yml =====



# ===== Dockerfile =====


# ===== database_init.py =====



# ===== run.py =====
