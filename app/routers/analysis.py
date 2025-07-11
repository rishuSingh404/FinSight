from fastapi import APIRouter, HTTPException, UploadFile, File
from app.services.analytics import AnalyticsService
from app.services.cache_service import cache_service
from app.services.enhanced_ml_predictor import EnhancedMLPredictor
import uuid

router = APIRouter()
analytics_service = AnalyticsService()
enhanced_ml_predictor = EnhancedMLPredictor()

@router.get("/analysis/{file_id}")
async def get_analysis(file_id: str):
    """Get analysis results for a file"""
    try:
        # Check cache first
        cached_result = cache_service.get_cached_analysis(file_id)
        if cached_result:
            return {
                "message": "Analysis results retrieved from cache",
                "cached": True,
                "file_id": file_id,
                **cached_result
            }
        
        # Perform analysis
        result = analytics_service.analyze_file(file_id)
        
        # Cache the result
        cache_service.cache_analysis_result(file_id, result)
        
        return {
            "message": "Analysis completed successfully",
            "cached": False,
            "file_id": file_id,
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analysis/{file_id}")
async def force_analysis(file_id: str):
    """Force re-run analysis for a file"""
    try:
        # Clear cache for this file
        cache_service.invalidate_file_cache(file_id)
        
        # Perform analysis
        result = analytics_service.analyze_file(file_id)
        
        # Cache the new result
        cache_service.cache_analysis_result(file_id, result)
        
        return {
            "message": "Analysis re-run completed successfully",
            "file_id": file_id,
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{file_id}/enhanced")
async def get_enhanced_analysis(file_id: str):
    """Get enhanced analysis with ML insights"""
    try:
        # Check cache first
        cache_key = f"enhanced_analysis_{file_id}"
        cached_result = cache_service.get(cache_key)
        if cached_result:
            return {
                "message": "Enhanced analysis results retrieved from cache",
                "cached": True,
                "file_id": file_id,
                **cached_result
            }
        
        # Get file path
        file_path = analytics_service.get_file_path(file_id)
        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Perform enhanced analysis
        enhanced_result = enhanced_ml_predictor.predict_risk(file_path)
        
        # Cache the result
        cache_service.set(cache_key, enhanced_result, expire=3600)
        
        return {
            "message": "Enhanced analysis completed successfully",
            "cached": False,
            "file_id": file_id,
            **enhanced_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_file(request: dict):
    """Analyze a file with specified analysis type"""
    try:
        file_id = request.get("file_id")
        analysis_type = request.get("analysis_type", "basic")
        
        if not file_id:
            raise HTTPException(status_code=400, detail="file_id is required")
        
        # Check cache first
        cache_key = f"analysis_{analysis_type}_{file_id}"
        cached_result = cache_service.get(cache_key)
        if cached_result:
            return {
                "message": f"{analysis_type} analysis results retrieved from cache",
                "cached": True,
                "file_id": file_id,
                "analysis_type": analysis_type,
                **cached_result
            }
        
        # Perform analysis based on type
        if analysis_type == "basic":
            result = analytics_service.analyze_file(file_id)
        elif analysis_type == "sentiment":
            result = analytics_service.analyze_sentiment(file_id)
        elif analysis_type == "topic":
            result = analytics_service.analyze_topics(file_id)
        elif analysis_type == "summary":
            result = analytics_service.analyze_summary(file_id)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown analysis type: {analysis_type}")
        
        # Cache the result
        cache_service.set(cache_key, result, expire=3600)
        
        return {
            "message": f"{analysis_type} analysis completed successfully",
            "cached": False,
            "file_id": file_id,
            "analysis_type": analysis_type,
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{file_id}/summary")
async def get_analysis_summary(file_id: str):
    """Get analysis summary with key metrics"""
    try:
        # Get basic analysis
        analysis_result = await get_analysis(file_id)
        
        # Extract key metrics
        summary = {
            "file_id": file_id,
            "file_type": analysis_result.get("file_type", "unknown"),
            "data_quality_score": analysis_result.get("eda_results", {}).get("data_quality_score", 0),
            "total_rows": analysis_result.get("summary_stats", {}).get("rows", 0),
            "total_columns": analysis_result.get("summary_stats", {}).get("columns", 0),
            "missing_data_percentage": 0,
            "outliers_detected": 0
        }
        
        # Calculate missing data percentage
        missing_values = analysis_result.get("summary_stats", {}).get("missing_values", {})
        if missing_values:
            total_cells = summary["total_rows"] * summary["total_columns"]
            missing_cells = sum(missing_values.values())
            summary["missing_data_percentage"] = (missing_cells / total_cells * 100) if total_cells > 0 else 0
        
        # Count outliers
        outliers = analysis_result.get("eda_results", {}).get("outliers_info", {})
        summary["outliers_detected"] = len(outliers)
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 