from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import json
from datetime import datetime

from app.database.connection import get_db
from app.models.database import File as FileModel, AnalysisResult
from app.models.schemas import AnalysisResponse
from app.services.analytics import AnalyticsService

router = APIRouter()

@router.get("/analysis/{file_id}", response_model=AnalysisResponse)
async def get_analysis(file_id: str, db: Session = Depends(get_db)):
    """
    Get analysis results for a specific file
    """
    try:
        # Check if file exists
        file_record = db.query(FileModel).filter(FileModel.id == file_id).first()
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check if analysis already exists
        existing_analysis = db.query(AnalysisResult).filter(
            AnalysisResult.file_id == file_id
        ).first()
        
        if existing_analysis:
            # Return existing analysis
            return AnalysisResponse(
                file_id=file_id,
                summary_stats=json.loads(existing_analysis.summary_stats),
                eda_results=json.loads(existing_analysis.eda_results),
                created_at=existing_analysis.created_at
            )
        
        # Perform new analysis
        analytics_service = AnalyticsService()
        analysis_results = analytics_service.perform_eda(file_record.file_path)
        
        # Save analysis results
        new_analysis = AnalysisResult(
            file_id=file_id,
            summary_stats=json.dumps(analysis_results["summary_stats"]),
            eda_results=json.dumps(analysis_results["eda_results"])
        )
        
        db.add(new_analysis)
        db.commit()
        db.refresh(new_analysis)
        
        return AnalysisResponse(
            file_id=file_id,
            summary_stats=analysis_results["summary_stats"],
            eda_results=analysis_results["eda_results"],
            created_at=new_analysis.created_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/analysis/{file_id}")
async def run_analysis(file_id: str, db: Session = Depends(get_db)):
    """
    Force run analysis for a specific file (overwrites existing)
    """
    try:
        # Check if file exists
        file_record = db.query(FileModel).filter(FileModel.id == file_id).first()
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete existing analysis if any
        db.query(AnalysisResult).filter(AnalysisResult.file_id == file_id).delete()
        
        # Perform new analysis
        analytics_service = AnalyticsService()
        analysis_results = analytics_service.perform_eda(file_record.file_path)
        
        # Save analysis results
        new_analysis = AnalysisResult(
            file_id=file_id,
            summary_stats=json.dumps(analysis_results["summary_stats"]),
            eda_results=json.dumps(analysis_results["eda_results"])
        )
        
        db.add(new_analysis)
        db.commit()
        
        return {
            "message": "Analysis completed successfully",
            "file_id": file_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}") 