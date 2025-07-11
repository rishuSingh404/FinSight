from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import os
import uuid
from datetime import datetime
import aiofiles

from app.database.connection import get_db
from app.models.database import File as FileModel
from app.models.schemas import FileUploadResponse
from app.utils.config import settings
from app.services.file_processor import FileProcessor

router = APIRouter()

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a financial data file (CSV, PDF, etc.)
    """
    try:
        # Validate file type
        allowed_extensions = ['.csv', '.pdf', '.txt']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Create file path
        file_path = os.path.join(settings.UPLOAD_PATH, f"{file_id}_{file.filename}")
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Get file size
        file_size = len(content)
        
        # Save to database
        db_file = FileModel(
            id=file_id,
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            content_type=file.content_type,
            status="uploaded"
        )
        
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        return FileUploadResponse(
            file_id=file_id,
            filename=file.filename,
            status="uploaded",
            message="File uploaded successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/files/{file_id}")
async def get_file_info(file_id: str, db: Session = Depends(get_db)):
    """
    Get information about an uploaded file
    """
    file_record = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "file_id": file_record.id,
        "filename": file_record.filename,
        "status": file_record.status,
        "upload_date": file_record.upload_date,
        "file_size": file_record.file_size
    } 