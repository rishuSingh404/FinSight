from fastapi import APIRouter, HTTPException, UploadFile, File
from app.services.file_processor import FileProcessor
from app.services.cache_service import cache_service
import uuid
import os
from app.utils.config import settings

router = APIRouter()
file_processor = FileProcessor()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a financial data file"""
    try:
        # Validate file size
        if file.size and file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE / (1024*1024)}MB"
            )
        
        # Validate file type
        allowed_extensions = ['.csv', '.txt', '.pdf', '.xlsx', '.xls']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Save file
        file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}_{file.filename}")
        
        # Ensure upload directory exists
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process file to get metadata
        try:
            processed_data = file_processor.process_file(file_path)
            file_type = processed_data.get("file_type", "unknown")
            data_preview = processed_data.get("data_preview", {})
        except Exception as e:
            file_type = "unknown"
            data_preview = {}
        
        # Store file metadata in cache
        metadata = {
            "file_id": file_id,
            "filename": file.filename,
            "file_path": file_path,
            "file_size": file.size,
            "file_type": file_type,
            "upload_timestamp": str(uuid.uuid4()),  # Simplified timestamp
            "data_preview": data_preview
        }
        
        cache_service.cache_file_metadata(file_id, metadata)
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "status": "uploaded",
            "message": "File uploaded successfully",
            "file_type": file_type,
            "file_size": file.size
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/files/{file_id}")
async def get_file_info(file_id: str):
    """Get file information"""
    try:
        # Get cached metadata
        metadata = cache_service.get_cached_metadata(file_id)
        
        if not metadata:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check if file still exists
        if not os.path.exists(metadata["file_path"]):
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        return {
            "file_id": file_id,
            "filename": metadata["filename"],
            "file_size": metadata["file_size"],
            "file_type": metadata["file_type"],
            "upload_timestamp": metadata["upload_timestamp"],
            "data_preview": metadata.get("data_preview", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get file info: {str(e)}")

@router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """Delete a file"""
    try:
        # Get cached metadata
        metadata = cache_service.get_cached_metadata(file_id)
        
        if not metadata:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete file from disk
        if os.path.exists(metadata["file_path"]):
            os.remove(metadata["file_path"])
        
        # Clear cache
        cache_service.invalidate_file_cache(file_id)
        
        return {
            "message": "File deleted successfully",
            "file_id": file_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@router.get("/files")
async def list_files():
    """List all uploaded files"""
    try:
        # This would typically query a database
        # For now, we'll return a simple response
        return {
            "message": "File listing endpoint",
            "note": "In a full implementation, this would return all uploaded files"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}") 