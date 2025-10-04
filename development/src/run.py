"""
Development runner script
"""
import uvicorn
import asyncio
from database_init import initialize_database

async def startup():
    """Startup tasks"""
    print("🚀 Starting RAG Chatbot API...")
    
    # Initialize database if needed
    try:
        await initialize_database()
    except Exception as e:
        print(f"Database initialization warning: {e}")
    
    print("✅ Startup complete!")

if __name__ == "__main__":
    # Run startup tasks
    asyncio.run(startup())
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )