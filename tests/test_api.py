import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
import tempfile

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_upload_endpoint():
    """Test file upload endpoint"""
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("column1,column2\n1,2\n3,4")
        temp_file_path = f.name
    
    try:
        with open(temp_file_path, 'rb') as f:
            response = client.post(
                "/api/v1/upload",
                files={"file": ("test.csv", f, "text/csv")}
            )
        
        assert response.status_code == 200
        result = response.json()
        assert "file_id" in result
        assert "filename" in result
        assert result["status"] == "uploaded"
        
        # Store file_id for other tests
        file_id = result["file_id"]
        
        # Test getting file info
        response = client.get(f"/api/v1/files/{file_id}")
        assert response.status_code == 200
        assert response.json()["file_id"] == file_id
        
    finally:
        # Clean up
        os.unlink(temp_file_path)

def test_analysis_endpoint():
    """Test analysis endpoint"""
    # First upload a file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("column1,column2\n1,2\n3,4")
        temp_file_path = f.name
    
    try:
        with open(temp_file_path, 'rb') as f:
            upload_response = client.post(
                "/api/v1/upload",
                files={"file": ("test.csv", f, "text/csv")}
            )
        
        file_id = upload_response.json()["file_id"]
        
        # Test analysis endpoint
        response = client.get(f"/api/v1/analysis/{file_id}")
        assert response.status_code == 200
        result = response.json()
        assert "summary_stats" in result
        assert "eda_results" in result
        
    finally:
        os.unlink(temp_file_path)

def test_prediction_endpoint():
    """Test prediction endpoint"""
    # First upload a file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("column1,column2\n1,2\n3,4")
        temp_file_path = f.name
    
    try:
        with open(temp_file_path, 'rb') as f:
            upload_response = client.post(
                "/api/v1/upload",
                files={"file": ("test.csv", f, "text/csv")}
            )
        
        file_id = upload_response.json()["file_id"]
        
        # Test prediction endpoint
        response = client.post(f"/api/v1/predict/{file_id}")
        assert response.status_code == 200
        result = response.json()
        assert "risk_score" in result
        assert "confidence" in result
        assert "prediction_data" in result
        
    finally:
        os.unlink(temp_file_path)

def test_invalid_file_upload():
    """Test upload with invalid file type"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is not a CSV file")
        temp_file_path = f.name
    
    try:
        with open(temp_file_path, 'rb') as f:
            response = client.post(
                "/api/v1/upload",
                files={"file": ("test.txt", f, "text/plain")}
            )
        
        # Should still work for txt files
        assert response.status_code == 200
        
    finally:
        os.unlink(temp_file_path)

def test_nonexistent_file():
    """Test accessing non-existent file"""
    fake_file_id = "nonexistent-id"
    
    response = client.get(f"/api/v1/analysis/{fake_file_id}")
    assert response.status_code == 404
    
    response = client.post(f"/api/v1/predict/{fake_file_id}")
    assert response.status_code == 404 