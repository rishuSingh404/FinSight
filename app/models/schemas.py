from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    status: str
    message: str

class AnalysisRequest(BaseModel):
    file_id: str

class AnalysisResponse(BaseModel):
    file_id: str
    summary_stats: Dict[str, Any]
    eda_results: Dict[str, Any]
    created_at: datetime

class PredictionRequest(BaseModel):
    file_id: str

class PredictionResponse(BaseModel):
    file_id: str
    risk_score: float
    confidence: float
    prediction_data: Dict[str, Any]
    created_at: datetime

class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int 