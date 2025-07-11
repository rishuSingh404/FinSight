import pandas as pd
import numpy as np
from typing import Dict, Any
import os
from app.services.file_processor import FileProcessor

class MLPredictor:
    """Service for ML-based risk prediction"""
    
    def __init__(self):
        self.file_processor = FileProcessor()
        # Initialize models (simplified for now)
        self.sentiment_model = None
        self.summarizer = None
        
    def predict_risk(self, file_path: str) -> Dict[str, Any]:
        """
        Predict financial risk based on uploaded file
        """
        try:
            # Process the file
            processed_data = self.file_processor.process_file(file_path)
            
            if processed_data["file_type"] == "csv":
                return self._predict_from_csv(processed_data["data"])
            elif processed_data["file_type"] == "txt":
                return self._predict_from_text(processed_data["data"])
            else:
                return self._predict_generic(processed_data)
                
        except Exception as e:
            raise Exception(f"Risk prediction failed: {str(e)}")
    
    def _predict_from_csv(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Predict risk from CSV data"""
        try:
            # Basic risk indicators from financial data
            risk_indicators = {}
            
            # Check for numeric columns that might indicate risk
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) > 0:
                # Calculate basic risk metrics
                for col in numeric_cols:
                    if 'debt' in col.lower() or 'liability' in col.lower():
                        risk_indicators[f"{col}_risk"] = self._calculate_debt_risk(df[col])
                    elif 'revenue' in col.lower() or 'income' in col.lower():
                        risk_indicators[f"{col}_risk"] = self._calculate_revenue_risk(df[col])
                    elif 'ratio' in col.lower():
                        risk_indicators[f"{col}_risk"] = self._calculate_ratio_risk(df[col])
            
            # Calculate overall risk score
            risk_score = self._calculate_overall_risk_score(risk_indicators)
            confidence = self._calculate_confidence(df)
            
            return {
                "risk_score": risk_score,
                "confidence": confidence,
                "prediction_data": {
                    "risk_indicators": risk_indicators,
                    "data_quality": self._assess_data_quality(df),
                    "risk_factors": self._identify_risk_factors(df)
                }
            }
            
        except Exception as e:
            raise Exception(f"CSV prediction failed: {str(e)}")
    
    def _predict_from_text(self, text: str) -> Dict[str, Any]:
        """Predict risk from text data (10-K reports, etc.)"""
        try:
            # Basic sentiment analysis
            sentiment_score = self._analyze_sentiment(text)
            
            # Extract risk-related keywords
            risk_keywords = self._extract_risk_keywords(text)
            
            # Calculate risk score based on sentiment and keywords
            risk_score = self._calculate_text_risk_score(sentiment_score, risk_keywords)
            confidence = self._calculate_text_confidence(text)
            
            return {
                "risk_score": risk_score,
                "confidence": confidence,
                "prediction_data": {
                    "sentiment_score": sentiment_score,
                    "risk_keywords": risk_keywords,
                    "text_analysis": self._analyze_text_content(text)
                }
            }
            
        except Exception as e:
            raise Exception(f"Text prediction failed: {str(e)}")
    
    def _predict_generic(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generic prediction for unsupported file types"""
        return {
            "risk_score": 0.5,  # Neutral risk
            "confidence": 0.1,  # Low confidence
            "prediction_data": {
                "message": "Limited analysis available for this file type",
                "file_type": data.get("file_type", "unknown")
            }
        }
    
    def _calculate_debt_risk(self, debt_series: pd.Series) -> float:
        """Calculate risk based on debt levels"""
        if debt_series.isnull().all():
            return 0.5
        
        # Simple debt risk calculation
        avg_debt = debt_series.mean()
        debt_volatility = debt_series.std()
        
        # Higher debt and volatility = higher risk
        risk = min(1.0, (avg_debt / 1000000 + debt_volatility / 100000) / 2)
        return round(risk, 3)
    
    def _calculate_revenue_risk(self, revenue_series: pd.Series) -> float:
        """Calculate risk based on revenue patterns"""
        if revenue_series.isnull().all():
            return 0.5
        
        # Revenue decline = higher risk
        if len(revenue_series) > 1:
            revenue_change = (revenue_series.iloc[-1] - revenue_series.iloc[0]) / revenue_series.iloc[0]
            risk = max(0.0, min(1.0, 0.5 - revenue_change))
        else:
            risk = 0.5
        
        return round(risk, 3)
    
    def _calculate_ratio_risk(self, ratio_series: pd.Series) -> float:
        """Calculate risk based on financial ratios"""
        if ratio_series.isnull().all():
            return 0.5
        
        # Extreme ratios = higher risk
        mean_ratio = ratio_series.mean()
        std_ratio = ratio_series.std()
        
        # Calculate how far ratios deviate from mean
        risk = min(1.0, std_ratio / (abs(mean_ratio) + 1e-6))
        return round(risk, 3)
    
    def _calculate_overall_risk_score(self, risk_indicators: Dict[str, float]) -> float:
        """Calculate overall risk score from individual indicators"""
        if not risk_indicators:
            return 0.5
        
        # Weighted average of risk indicators
        total_risk = sum(risk_indicators.values())
        avg_risk = total_risk / len(risk_indicators)
        
        return round(avg_risk, 3)
    
    def _calculate_confidence(self, df: pd.DataFrame) -> float:
        """Calculate confidence in prediction based on data quality"""
        # More data and fewer missing values = higher confidence
        data_completeness = 1 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))
        data_volume = min(1.0, len(df) / 1000)  # Normalize to 0-1
        
        confidence = (data_completeness + data_volume) / 2
        return round(confidence, 3)
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess the quality of the data"""
        return {
            "completeness": 1 - (df.isnull().sum().sum() / (len(df) * len(df.columns))),
            "consistency": self._check_data_consistency(df),
            "timeliness": "unknown"  # Would need timestamp data
        }
    
    def _check_data_consistency(self, df: pd.DataFrame) -> float:
        """Check data consistency"""
        # Simple consistency check - variance in numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return 1.0
        
        consistency_scores = []
        for col in numeric_cols:
            if df[col].std() > 0:
                consistency_scores.append(1.0)
            else:
                consistency_scores.append(0.5)
        
        return np.mean(consistency_scores) if consistency_scores else 1.0
    
    def _identify_risk_factors(self, df: pd.DataFrame) -> list:
        """Identify potential risk factors in the data"""
        risk_factors = []
        
        # Check for missing data
        missing_cols = df.columns[df.isnull().sum() > 0]
        if len(missing_cols) > 0:
            risk_factors.append(f"Missing data in {len(missing_cols)} columns")
        
        # Check for extreme values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].std() > df[col].mean() * 2:  # High volatility
                risk_factors.append(f"High volatility in {col}")
        
        return risk_factors
    
    def _analyze_sentiment(self, text: str) -> float:
        """Basic sentiment analysis"""
        positive_words = ['good', 'great', 'excellent', 'positive', 'profit', 'growth', 'increase', 'success']
        negative_words = ['bad', 'poor', 'negative', 'loss', 'decline', 'decrease', 'risk', 'failure', 'debt']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return 0.5
        
        sentiment_score = positive_count / total_sentiment_words
        return round(sentiment_score, 3)
    
    def _extract_risk_keywords(self, text: str) -> Dict[str, int]:
        """Extract risk-related keywords"""
        risk_keywords = [
            'risk', 'debt', 'loss', 'decline', 'decrease', 'failure', 'default',
            'bankruptcy', 'liquidation', 'restructuring', 'write-off', 'impairment'
        ]
        
        text_lower = text.lower()
        keyword_counts = {}
        
        for keyword in risk_keywords:
            count = text_lower.count(keyword)
            if count > 0:
                keyword_counts[keyword] = count
        
        return keyword_counts
    
    def _calculate_text_risk_score(self, sentiment_score: float, risk_keywords: Dict[str, int]) -> float:
        """Calculate risk score from text analysis"""
        # Lower sentiment = higher risk
        sentiment_risk = 1 - sentiment_score
        
        # More risk keywords = higher risk
        keyword_risk = min(1.0, sum(risk_keywords.values()) / 10)
        
        # Combine both factors
        overall_risk = (sentiment_risk + keyword_risk) / 2
        return round(overall_risk, 3)
    
    def _calculate_text_confidence(self, text: str) -> float:
        """Calculate confidence in text-based prediction"""
        # Longer text = higher confidence (up to a point)
        word_count = len(text.split())
        confidence = min(1.0, word_count / 1000)
        return round(confidence, 3)
    
    def _analyze_text_content(self, text: str) -> Dict[str, Any]:
        """Analyze text content for risk assessment"""
        return {
            "word_count": len(text.split()),
            "sentence_count": len(text.split('.')),
            "risk_keyword_density": len(self._extract_risk_keywords(text)) / len(text.split()) * 1000,
            "complexity_score": self._calculate_text_complexity(text)
        }
    
    def _calculate_text_complexity(self, text: str) -> float:
        """Calculate text complexity score"""
        words = text.split()
        if not words:
            return 0.0
        
        avg_word_length = np.mean([len(word) for word in words])
        unique_word_ratio = len(set(words)) / len(words)
        
        complexity = (avg_word_length + unique_word_ratio) / 2
        return round(complexity, 3) 