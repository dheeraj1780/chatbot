from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from controller.login_controller import login_router
from controller.document_controller import document_router
from controller.user_query_controller import query_router
import uvicorn
import asyncio
from database_init import initialize_database, create_admin_user

app = FastAPI(
    title="Enhanced RAG Chatbot API",
    description="Document-based Q&A system with group filtering",
    version="1.0.0"
)

async def startup():
    """Startup tasks"""
    print("🚀 Starting RAG Chatbot API...")
    
    # Initialize database if needed
    try:
        await initialize_database()
        await create_admin_user()
    except Exception as e:
        print(f"Database initialization warning: {e}")
    
    print("✅ Startup complete!")


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(login_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(document_router, prefix="/api/documents", tags=["Document Management"])
app.include_router(query_router, prefix="/api/query", tags=["Query & Chat"])

@app.get("/")
async def root():
    return {"message": "Enhanced RAG Chatbot API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    asyncio.run(startup())
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
