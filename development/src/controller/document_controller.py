from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import List, Optional
from service.document_service import DocumentService
from service.auth_service import AuthService
from pydantic import BaseModel

document_router = APIRouter()

class GroupCreateRequest(BaseModel):
    name: str
    description: str

class GroupResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: str

class DocumentResponse(BaseModel):
    id: int
    filename: str
    group_id: int
    group_name: str
    uploaded_at: str

@document_router.post("/groups", response_model=GroupResponse)
async def create_group(
    request: GroupCreateRequest,
    current_user: dict = Depends(AuthService.get_current_admin_user)
):
    """Create a new document group"""
    try:
        document_service = DocumentService()
        group = await document_service.create_document_group(request.name, request.description)
        return group
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@document_router.get("/groups", response_model=List[GroupResponse])
async def list_groups(
    current_user: dict = Depends(AuthService.get_current_user)
):
    """List all document groups"""
    try:
        document_service = DocumentService()
        groups = await document_service.get_all_groups()
        return groups
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@document_router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    group_id: int = Form(...),
    current_user: dict = Depends(AuthService.get_current_admin_user)
):
    """Upload and process a document"""
    try:
        document_service = DocumentService()
        result = await document_service.upload_and_process_document(file, group_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@document_router.get("/groups/{group_id}/documents", response_model=List[DocumentResponse])
async def get_group_documents(
    group_id: int,
    current_user: dict = Depends(AuthService.get_current_user)
):
    """Get all documents in a specific group"""
    try:
        document_service = DocumentService()
        documents = await document_service.get_documents_by_group(group_id)
        return documents
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@document_router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    current_user: dict = Depends(AuthService.get_current_admin_user)
):
    """Delete a document and its chunks"""
    try:
        document_service = DocumentService()
        await document_service.delete_document(document_id)
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))