from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from repository.orm import UserRepository
from utils.db_connection import get_db_session
import jwt
from datetime import datetime, timedelta
import bcrypt

security = HTTPBearer()

class AuthService:
    def __init__(self):
        self.secret_key = "cdf2ecdbf62b1cd112a22392faa54a47"
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30

    async def authenticate_user(self, username: str, password: str):
        """Authenticate user and return JWT token"""
        async with get_db_session() as session:
            user_repo = UserRepository(session)
            user = await user_repo.get_user_by_username(username)
            
            if not user or not self._verify_password(password, user.password_hash):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            access_token = self._create_access_token(
                data={"sub": user.username, "user_id": user.id, "role": user.role}
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": user.id,
                "role": user.role
            }

    def _create_access_token(self, data: dict, expires_delta: timedelta = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Get current authenticated user"""
        try:
            auth_service = AuthService()
            payload = jwt.decode(credentials.credentials, auth_service.secret_key, algorithms=[auth_service.algorithm])
            username: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            role: str = payload.get("role")
            
            if username is None:
                raise HTTPException(status_code=401, detail="Invalid token")
                
            return {"username": username, "user_id": user_id, "role": role}
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    @staticmethod
    def get_current_admin_user(current_user: dict = Depends(get_current_user)):
        """Get current user and verify admin role"""
        if current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        return current_user

    async def logout_user(self, token: str):
        """Logout user (in production, add token to blacklist)"""
        # In production, implement token blacklisting
        pass


# ===== service/document_service.py =====


# ===== service/query_service.py =====


# ===== repository/orm.py =====
