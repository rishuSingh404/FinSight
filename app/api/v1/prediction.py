from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import json
from datetime import datetime

from app.database.connection import get_db
from app.models.database import File as FileModel, Prediction
from app.models.schemas import PredictionResponse
from app.services.ml_predictor import MLPredictor

router = APIRouter()

@router.post("/predict/{file_id}", response_model=PredictionResponse)
async def get_prediction(file_id: str, db: Session = Depends(get_db)):
    """
    Get ML prediction results for a specific file
    """
    try:
        # Check if file exists
        file_record = db.query(FileModel).filter(FileModel.id == file_id).first()
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check if prediction already exists
        existing_prediction = db.query(Prediction).filter(
            Prediction.file_id == file_id
        ).first()
        
        if existing_prediction:
            # Return existing prediction
            return PredictionResponse(
                file_id=file_id,
                risk_score=existing_prediction.risk_score,
                confidence=existing_prediction.confidence,
                prediction_data=json.loads(existing_prediction.prediction_data),
                created_at=existing_prediction.created_at
            )
        
        # Perform new prediction
        ml_predictor = MLPredictor()
        prediction_results = ml_predictor.predict_risk(file_record.file_path)
        
        # Save prediction results
        new_prediction = Prediction(
            file_id=file_id,
            risk_score=prediction_results["risk_score"],
            confidence=prediction_results["confidence"],
            prediction_data=json.dumps(prediction_results["prediction_data"])
        )
        
        db.add(new_prediction)
        db.commit()
        db.refresh(new_prediction)
        
        return PredictionResponse(
            file_id=file_id,
            risk_score=prediction_results["risk_score"],
            confidence=prediction_results["confidence"],
            prediction_data=prediction_results["prediction_data"],
            created_at=new_prediction.created_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/predict/{file_id}/force")
async def force_prediction(file_id: str, db: Session = Depends(get_db)):
    """
    Force run prediction for a specific file (overwrites existing)
    """
    try:
        # Check if file exists
        file_record = db.query(FileModel).filter(FileModel.id == file_id).first()
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete existing prediction if any
        db.query(Prediction).filter(Prediction.file_id == file_id).delete()
        
        # Perform new prediction
        ml_predictor = MLPredictor()
        prediction_results = ml_predictor.predict_risk(file_record.file_path)
        
        # Save prediction results
        new_prediction = Prediction(
            file_id=file_id,
            risk_score=prediction_results["risk_score"],
            confidence=prediction_results["confidence"],
            prediction_data=json.dumps(prediction_results["prediction_data"])
        )
        
        db.add(new_prediction)
        db.commit()
        
        return {
            "message": "Prediction completed successfully",
            "file_id": file_id,
            "risk_score": prediction_results["risk_score"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}") 