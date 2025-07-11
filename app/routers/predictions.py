from fastapi import APIRouter, HTTPException
from app.services.ml_predictor import MLPredictor
from app.services.enhanced_ml_predictor import EnhancedMLPredictor
from app.services.cache_service import cache_service
from app.services.analytics import AnalyticsService

router = APIRouter()
ml_predictor = MLPredictor()
enhanced_ml_predictor = EnhancedMLPredictor()
analytics_service = AnalyticsService()

@router.post("/predict/{file_id}")
async def get_prediction(file_id: str):
    """Get risk prediction for a file"""
    try:
        # Check cache first
        cached_result = cache_service.get_cached_prediction(file_id)
        if cached_result:
            return {
                "message": "Prediction results retrieved from cache",
                "cached": True,
                "file_id": file_id,
                **cached_result
            }
        
        # Get file path
        file_path = analytics_service.get_file_path(file_id)
        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Perform prediction
        result = ml_predictor.predict_risk(file_path)
        
        # Cache the result
        cache_service.cache_prediction_result(file_id, result)
        
        return {
            "message": "Prediction completed successfully",
            "cached": False,
            "file_id": file_id,
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict/{file_id}/force")
async def force_prediction(file_id: str):
    """Force re-run prediction for a file"""
    try:
        # Clear cache for this file
        cache_service.invalidate_file_cache(file_id)
        
        # Get file path
        file_path = analytics_service.get_file_path(file_id)
        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Perform prediction
        result = ml_predictor.predict_risk(file_path)
        
        # Cache the new result
        cache_service.cache_prediction_result(file_id, result)
        
        return {
            "message": "Prediction re-run completed successfully",
            "file_id": file_id,
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict/{file_id}/enhanced")
async def get_enhanced_prediction(file_id: str):
    """Get enhanced risk prediction with advanced ML analysis"""
    try:
        # Check cache first
        cache_key = f"enhanced_prediction_{file_id}"
        cached_result = cache_service.get(cache_key)
        if cached_result:
            return {
                "message": "Enhanced prediction results retrieved from cache",
                "cached": True,
                "file_id": file_id,
                **cached_result
            }
        
        # Get file path
        file_path = analytics_service.get_file_path(file_id)
        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Perform enhanced prediction
        enhanced_result = enhanced_ml_predictor.predict_risk(file_path)
        
        # Cache the result
        cache_service.set(cache_key, enhanced_result, expire=3600)
        
        return {
            "message": "Enhanced prediction completed successfully",
            "cached": False,
            "file_id": file_id,
            **enhanced_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predict/{file_id}/summary")
async def get_prediction_summary(file_id: str):
    """Get prediction summary with key risk metrics"""
    try:
        # Get basic prediction
        prediction_result = await get_prediction(file_id)
        
        # Extract key metrics
        summary = {
            "file_id": file_id,
            "risk_score": prediction_result.get("risk_score", 0),
            "confidence": prediction_result.get("confidence", 0),
            "risk_level": "Low",
            "confidence_level": "Low",
            "key_risk_factors": [],
            "recommendations": []
        }
        
        # Determine risk level
        risk_score = summary["risk_score"]
        if risk_score < 0.3:
            summary["risk_level"] = "Low"
        elif risk_score < 0.7:
            summary["risk_level"] = "Medium"
        else:
            summary["risk_level"] = "High"
        
        # Determine confidence level
        confidence = summary["confidence"]
        if confidence > 0.7:
            summary["confidence_level"] = "High"
        elif confidence > 0.4:
            summary["confidence_level"] = "Medium"
        else:
            summary["confidence_level"] = "Low"
        
        # Extract risk factors and recommendations
        prediction_data = prediction_result.get("prediction_data", {})
        summary["key_risk_factors"] = prediction_data.get("risk_factors", [])
        summary["recommendations"] = prediction_data.get("recommendations", [])
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict")
async def predict_file(request: dict):
    """Predict risk for a file with specified prediction type"""
    try:
        file_id = request.get("file_id")
        prediction_type = request.get("prediction_type", "risk_assessment")
        
        if not file_id:
            raise HTTPException(status_code=400, detail="file_id is required")
        
        # Check cache first
        cache_key = f"prediction_{prediction_type}_{file_id}"
        cached_result = cache_service.get(cache_key)
        if cached_result:
            return {
                "message": f"{prediction_type} prediction results retrieved from cache",
                "cached": True,
                "file_id": file_id,
                "prediction_type": prediction_type,
                **cached_result
            }
        
        # Get file path
        file_path = analytics_service.get_file_path(file_id)
        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Perform prediction based on type
        if prediction_type == "risk_assessment":
            result = ml_predictor.predict_risk(file_path)
        elif prediction_type == "trend_prediction":
            result = enhanced_ml_predictor.predict_trends(file_path)
        elif prediction_type == "anomaly_detection":
            result = enhanced_ml_predictor.detect_anomalies(file_path)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown prediction type: {prediction_type}")
        
        # Cache the result
        cache_service.set(cache_key, result, expire=3600)
        
        return {
            "message": f"{prediction_type} prediction completed successfully",
            "cached": False,
            "file_id": file_id,
            "prediction_type": prediction_type,
            **result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predict/{file_id}/compare")
async def compare_predictions(file_id: str):
    """Compare basic vs enhanced predictions"""
    try:
        # Get both predictions
        basic_prediction = await get_prediction(file_id)
        enhanced_prediction = await get_enhanced_prediction(file_id)
        
        comparison = {
            "file_id": file_id,
            "basic_prediction": {
                "risk_score": basic_prediction.get("risk_score", 0),
                "confidence": basic_prediction.get("confidence", 0)
            },
            "enhanced_prediction": {
                "risk_score": enhanced_prediction.get("risk_score", 0),
                "confidence": enhanced_prediction.get("confidence", 0)
            },
            "differences": {
                "risk_score_diff": enhanced_prediction.get("risk_score", 0) - basic_prediction.get("risk_score", 0),
                "confidence_diff": enhanced_prediction.get("confidence", 0) - basic_prediction.get("confidence", 0)
            }
        }
        
        return comparison
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 