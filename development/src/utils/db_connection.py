from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
import os
from contextlib import asynccontextmanager
from repository.schema.schema import Base

class DatabaseConnection:
    _instance = None
    _engine = None
    _session_factory = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._engine is None:
            self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize database connection"""
        # Database configuration
        DB_USER = os.getenv("DB_USER", "postgres")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "admin")
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = os.getenv("DB_PORT", "5432")
        DB_NAME = os.getenv("DB_NAME", "rag_chatbot")
        
        DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        
        self._engine = create_async_engine(
            DATABASE_URL,
            poolclass=NullPool,  # For async operations
            echo=False,  # Set to True for SQL logging
            future=True
        )
        
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def create_tables(self):
        """Create all tables"""
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def drop_tables(self):
        """Drop all tables (use with caution!)"""
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    def get_session_factory(self):
        """Get session factory"""
        return self._session_factory
    
    async def close(self):
        """Close database connections"""
        if self._engine:
            await self._engine.dispose()

# Singleton instance
db_connection = DatabaseConnection()

@asynccontextmanager
async def get_db_session():
    """Get database session context manager"""
    session_factory = db_connection.get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
