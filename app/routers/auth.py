from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import timedelta
from app.services.auth import auth_service
from app.services.monitoring import monitoring_service

router = APIRouter()
security = HTTPBearer()

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user_info: dict

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login endpoint"""
    try:
        # Authenticate user
        user = auth_service.authenticate_user(request.username, request.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = auth_service.create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=30 * 60,  # 30 minutes in seconds
            user_info=user
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/register")
async def register(request: RegisterRequest):
    """Register endpoint (simplified for demo)"""
    try:
        # In a real application, you would:
        # 1. Check if user already exists
        # 2. Hash the password
        # 3. Store user in database
        # 4. Send verification email
        
        # For demo purposes, we'll just return success
        return {
            "message": "User registered successfully",
            "username": request.username,
            "email": request.email,
            "note": "This is a demo implementation"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.get("/me")
async def get_current_user_info(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user information"""
    try:
        payload = auth_service.verify_token(credentials.credentials)
        return {
            "username": payload.get("sub"),
            "token_info": payload
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/refresh")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Refresh access token"""
    try:
        # Verify current token
        payload = auth_service.verify_token(credentials.credentials)
        
        # Create new token
        access_token_expires = timedelta(minutes=30)
        new_access_token = auth_service.create_access_token(
            data={"sub": payload.get("sub")}, expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=30 * 60,
            user_info={"username": payload.get("sub")}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout endpoint (token invalidation would be implemented here)"""
    try:
        # In a real application, you would:
        # 1. Add token to blacklist
        # 2. Clear user session
        # 3. Log the logout event
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        ) 