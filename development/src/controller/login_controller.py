# ===== controller/login_controller.py =====
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from service.auth_service import AuthService
from pydantic import BaseModel

login_router = APIRouter()
security = HTTPBearer()

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    role: str

@login_router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Admin login endpoint"""
    try:
        auth_service = AuthService()
        result = await auth_service.authenticate_user(request.username, request.password)
        return result
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@login_router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout endpoint"""
    try:
        auth_service = AuthService()
        await auth_service.logout_user(credentials.credentials)
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))