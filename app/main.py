from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import time
from datetime import datetime

from app.routers import upload, analysis, predictions, auth, monitoring
from app.services.monitoring import monitoring_service, RequestMetrics
from app.services.cache_service import cache_service
from app.services.auth import auth_service
from app.utils.config import settings

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting up Financial Analytics API...")
    yield
    # Shutdown
    print("Shutting down Financial Analytics API...")

app = FastAPI(
    title="Financial Analytics API",
    description="Advanced Financial Data Analysis & Risk Prediction Platform",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request monitoring middleware
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    
    # Get client info
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Process request
    response = await call_next(request)
    
    # Calculate response time
    response_time = time.time() - start_time
    
    # Record metrics
    request_metrics = RequestMetrics(
        endpoint=str(request.url.path),
        method=request.method,
        status_code=response.status_code,
        response_time=response_time,
        timestamp=datetime.utcnow(),
        user_agent=user_agent,
        ip_address=client_ip,
        error_message=None if response.status_code < 400 else "HTTP Error"
    )
    
    monitoring_service.record_request(request_metrics)
    
    return response

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        payload = auth_service.verify_token(credentials.credentials)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = monitoring_service.get_health_status()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "services": {
            "cache": cache_service.cache_enabled,
            "monitoring": True,
            "auth": True
        },
        "health": health_status
    }

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(upload.router, prefix="/api/v1", tags=["File Upload"])
app.include_router(analysis.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(predictions.router, prefix="/api/v1", tags=["Predictions"])
app.include_router(monitoring.router, prefix="/api/v1", tags=["Monitoring"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Financial Analytics API",
        "version": "2.0.0",
        "description": "Advanced Financial Data Analysis & Risk Prediction Platform",
        "documentation": "/docs",
        "health": "/health",
        "features": [
            "File upload and processing",
            "Advanced data analysis",
            "ML-powered risk prediction",
            "Authentication and security",
            "Caching for performance",
            "Real-time monitoring",
            "Comprehensive API documentation"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 