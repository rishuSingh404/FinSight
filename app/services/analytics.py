import pandas as pd
import numpy as np
from typing import Dict, Any
import json
from app.services.file_processor import FileProcessor

class AnalyticsService:
    """Service for performing exploratory data analysis"""
    
    def __init__(self):
        self.file_processor = FileProcessor()
    
    def perform_eda(self, file_path: str) -> Dict[str, Any]:
        """
        Perform exploratory data analysis on uploaded file
        """
        try:
            # Process the file
            processed_data = self.file_processor.process_file(file_path)
            
            if processed_data["file_type"] == "csv":
                return self._analyze_csv_data(processed_data["data"])
            elif processed_data["file_type"] == "txt":
                return self._analyze_text_data(processed_data["data"])
            else:
                return self._analyze_generic_data(processed_data)
                
        except Exception as e:
            raise Exception(f"EDA failed: {str(e)}")
    
    def _analyze_csv_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze CSV data"""
        try:
            # Basic statistics
            summary_stats = {
                "rows": len(df),
                "columns": len(df.columns),
                "missing_values": df.isnull().sum().to_dict(),
                "data_types": df.dtypes.astype(str).to_dict(),
                "memory_usage": df.memory_usage(deep=True).sum()
            }
            
            # Numeric columns analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                summary_stats["numeric_summary"] = df[numeric_cols].describe().to_dict()
            
            # Categorical columns analysis
            categorical_cols = df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                summary_stats["categorical_summary"] = {}
                for col in categorical_cols:
                    summary_stats["categorical_summary"][col] = {
                        "unique_values": df[col].nunique(),
                        "most_common": df[col].value_counts().head(5).to_dict()
                    }
            
            # EDA results
            eda_results = {
                "correlation_matrix": self._get_correlation_matrix(df),
                "missing_data_heatmap": self._get_missing_data_info(df),
                "outliers_info": self._detect_outliers(df),
                "data_quality_score": self._calculate_data_quality_score(df)
            }
            
            return {
                "summary_stats": summary_stats,
                "eda_results": eda_results
            }
            
        except Exception as e:
            raise Exception(f"CSV analysis failed: {str(e)}")
    
    def _analyze_text_data(self, text: str) -> Dict[str, Any]:
        """Analyze text data"""
        try:
            words = text.split()
            sentences = text.split('.')
            
            summary_stats = {
                "total_characters": len(text),
                "total_words": len(words),
                "total_sentences": len(sentences),
                "average_word_length": np.mean([len(word) for word in words]) if words else 0,
                "average_sentence_length": np.mean([len(sent.split()) for sent in sentences if sent.strip()]) if sentences else 0
            }
            
            eda_results = {
                "word_frequency": self._get_word_frequency(words),
                "text_complexity": self._calculate_text_complexity(text),
                "sentiment_indicators": self._extract_sentiment_indicators(text)
            }
            
            return {
                "summary_stats": summary_stats,
                "eda_results": eda_results
            }
            
        except Exception as e:
            raise Exception(f"Text analysis failed: {str(e)}")
    
    def _analyze_generic_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze generic data types"""
        return {
            "summary_stats": {
                "file_type": data.get("file_type", "unknown"),
                "file_size": data.get("file_size", 0),
                "message": "Basic file information"
            },
            "eda_results": {
                "analysis_type": "basic",
                "message": "Advanced analysis not available for this file type"
            }
        }
    
    def _get_correlation_matrix(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get correlation matrix for numeric columns"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            return corr_matrix.to_dict()
        return {}
    
    def _get_missing_data_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get missing data information"""
        missing_data = df.isnull().sum()
        return {
            "missing_counts": missing_data.to_dict(),
            "missing_percentages": (missing_data / len(df) * 100).to_dict()
        }
    
    def _detect_outliers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect outliers in numeric columns"""
        outliers_info = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            outliers_info[col] = {
                "count": len(outliers),
                "percentage": len(outliers) / len(df) * 100
            }
        
        return outliers_info
    
    def _calculate_data_quality_score(self, df: pd.DataFrame) -> float:
        """Calculate overall data quality score"""
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        quality_score = (total_cells - missing_cells) / total_cells * 100
        return round(quality_score, 2)
    
    def _get_word_frequency(self, words: list) -> Dict[str, int]:
        """Get word frequency from text"""
        from collections import Counter
        word_freq = Counter(words)
        return dict(word_freq.most_common(20))
    
    def _calculate_text_complexity(self, text: str) -> Dict[str, float]:
        """Calculate text complexity metrics"""
        words = text.split()
        sentences = text.split('.')
        
        return {
            "avg_word_length": np.mean([len(word) for word in words]) if words else 0,
            "avg_sentence_length": np.mean([len(sent.split()) for sent in sentences if sent.strip()]) if sentences else 0,
            "unique_word_ratio": len(set(words)) / len(words) if words else 0
        }
    
    def _extract_sentiment_indicators(self, text: str) -> Dict[str, int]:
        """Extract basic sentiment indicators"""
        positive_words = ['good', 'great', 'excellent', 'positive', 'profit', 'growth', 'increase']
        negative_words = ['bad', 'poor', 'negative', 'loss', 'decline', 'decrease', 'risk']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        return {
            "positive_indicators": positive_count,
            "negative_indicators": negative_count,
            "sentiment_ratio": positive_count / (positive_count + negative_count) if (positive_count + negative_count) > 0 else 0.5
        } 