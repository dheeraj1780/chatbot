from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from service.query_service import QueryService
from service.auth_service import AuthService
from pydantic import BaseModel

query_router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    k: Optional[int] = 5

class QueryResponse(BaseModel):
    query: str
    answer: str
    group_used: Optional[str] = None
    chunks_found: int

@query_router.post("/ask", response_model=QueryResponse)
async def ask_question(
    request: QueryRequest,
    current_user: dict = Depends(AuthService.get_current_user)
):
    """Ask a question to the RAG system"""
    try:
        query_service = QueryService()
        result = await query_service.find_group(
            request.query,
            request.k
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@query_router.get("/groups/{group_id}/search")
async def search_in_group(
    group_id: int,
    query: str,
    k: int = 5,
    current_user: dict = Depends(AuthService.get_current_user)
):
    """Search for similar documents in a specific group"""
    try:
        query_service = QueryService()
        result = await query_service.similarity_search_in_group(group_id, query, k)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))