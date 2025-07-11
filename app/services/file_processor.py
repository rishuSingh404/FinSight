import pandas as pd
import os
from typing import Dict, Any

class FileProcessor:
    """Service for processing uploaded files"""
    
    def __init__(self):
        self.supported_extensions = ['.csv', '.pdf', '.txt']
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process uploaded file and extract data
        """
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.csv':
                return self._process_csv(file_path)
            elif file_extension == '.txt':
                return self._process_txt(file_path)
            elif file_extension == '.pdf':
                return self._process_pdf(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            raise Exception(f"File processing failed: {str(e)}")
    
    def _process_csv(self, file_path: str) -> Dict[str, Any]:
        """Process CSV files"""
        try:
            df = pd.read_csv(file_path)
            return {
                "data": df,
                "columns": df.columns.tolist(),
                "shape": df.shape,
                "file_type": "csv"
            }
        except Exception as e:
            raise Exception(f"CSV processing failed: {str(e)}")
    
    def _process_txt(self, file_path: str) -> Dict[str, Any]:
        """Process text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into lines for basic processing
            lines = content.split('\n')
            
            return {
                "data": content,
                "lines": lines,
                "word_count": len(content.split()),
                "char_count": len(content),
                "file_type": "txt"
            }
        except Exception as e:
            raise Exception(f"Text processing failed: {str(e)}")
    
    def _process_pdf(self, file_path: str) -> Dict[str, Any]:
        """Process PDF files - simplified version"""
        try:
            # For now, return basic info about PDF
            # In production, you'd use PyPDF2 or similar
            file_size = os.path.getsize(file_path)
            
            return {
                "data": f"PDF file: {os.path.basename(file_path)}",
                "file_size": file_size,
                "file_type": "pdf",
                "message": "PDF processing requires additional libraries"
            }
        except Exception as e:
            raise Exception(f"PDF processing failed: {str(e)}")
    
    def validate_file(self, file_path: str) -> bool:
        """Validate if file can be processed"""
        if not os.path.exists(file_path):
            return False
        
        file_extension = os.path.splitext(file_path)[1].lower()
        return file_extension in self.supported_extensions 