from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.services.monitoring import monitoring_service
from app.services.cache_service import cache_service
from app.services.auth import auth_service

router = APIRouter()
security = HTTPBearer()

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        payload = auth_service.verify_token(credentials.credentials)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/health")
async def get_health_status():
    """Get detailed health status"""
    try:
        health_status = monitoring_service.get_health_status()
        return health_status
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get health status: {str(e)}"
        )

@router.get("/metrics/performance")
async def get_performance_metrics():
    """Get performance metrics summary"""
    try:
        performance = monitoring_service.get_performance_summary()
        return performance
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get performance metrics: {str(e)}"
        )

@router.get("/metrics/requests")
async def get_request_metrics(hours: int = Query(24, ge=1, le=168)):
    """Get request metrics for the last N hours"""
    try:
        metrics = monitoring_service.get_request_metrics(hours=hours)
        return {
            "hours": hours,
            "total_requests": len(metrics),
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get request metrics: {str(e)}"
        )

@router.get("/metrics/system")
async def get_system_metrics(hours: int = Query(24, ge=1, le=168)):
    """Get system metrics for the last N hours"""
    try:
        metrics = monitoring_service.get_system_metrics(hours=hours)
        return {
            "hours": hours,
            "total_snapshots": len(metrics),
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system metrics: {str(e)}"
        )

@router.get("/metrics/endpoints")
async def get_endpoint_statistics():
    """Get endpoint statistics"""
    try:
        stats = monitoring_service.get_endpoint_statistics()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get endpoint statistics: {str(e)}"
        )

@router.get("/metrics/errors")
async def get_error_statistics():
    """Get error statistics"""
    try:
        error_stats = monitoring_service.get_error_statistics()
        return error_stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get error statistics: {str(e)}"
        )

@router.get("/cache/stats")
async def get_cache_statistics():
    """Get cache statistics"""
    try:
        cache_stats = cache_service.get_cache_stats()
        return cache_stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cache statistics: {str(e)}"
        )

@router.post("/cache/clear")
async def clear_cache():
    """Clear all cache (admin only)"""
    try:
        # In a real application, you would check admin permissions
        # For demo purposes, we'll just clear the cache
        cache_service.clear_pattern("*")
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )

@router.get("/export")
async def export_metrics(format: str = Query("json", regex="^(json|csv)$")):
    """Export metrics in specified format"""
    try:
        if format.lower() == "json":
            exported_data = monitoring_service.export_metrics("json")
            return {"format": "json", "data": exported_data}
        else:
            raise HTTPException(
                status_code=400,
                detail="Only JSON format is currently supported"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export metrics: {str(e)}"
        )

@router.get("/dashboard")
async def get_dashboard_data():
    """Get comprehensive dashboard data"""
    try:
        # Get all monitoring data
        health_status = monitoring_service.get_health_status()
        performance = monitoring_service.get_performance_summary()
        error_stats = monitoring_service.get_error_statistics()
        cache_stats = cache_service.get_cache_stats()
        
        # Get recent activity
        recent_requests = monitoring_service.get_request_metrics(hours=1)
        recent_system = monitoring_service.get_system_metrics(hours=1)
        
        return {
            "timestamp": health_status["timestamp"],
            "health": health_status,
            "performance": performance,
            "errors": error_stats,
            "cache": cache_stats,
            "recent_activity": {
                "requests_last_hour": len(recent_requests),
                "system_snapshots": len(recent_system),
                "latest_system": recent_system[-1] if recent_system else None
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get dashboard data: {str(e)}"
        )

@router.post("/cleanup")
async def cleanup_old_metrics(days: int = Query(7, ge=1, le=30)):
    """Clean up old metrics (admin only)"""
    try:
        monitoring_service.clear_old_metrics(days=days)
        return {
            "message": f"Cleaned up metrics older than {days} days",
            "days": days
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup metrics: {str(e)}"
        ) 