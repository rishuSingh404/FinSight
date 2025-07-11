import pandas as pd
import numpy as np
from typing import Dict, Any, List
import os
import json
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from app.services.file_processor import FileProcessor

class EnhancedMLPredictor:
    """Enhanced ML predictor with integration to existing models"""
    
    def __init__(self):
        self.file_processor = FileProcessor()
        
        # Initialize models (will be loaded on demand)
        self.sentiment_model = None
        self.summarizer = None
        self.classifier = None
        
        # Model paths (relative to your existing models)
        self.model_paths = {
            "sentiment": "./models/distilbert-sentiment",
            "summarizer": "./models/distilbart-summarizer",
            "classifier": "./models/distilbert-classifier"
        }
        
        # Risk indicators and weights
        self.risk_indicators = {
            "financial_ratios": {
                "debt_to_equity": {"weight": 0.3, "threshold": 2.0},
                "current_ratio": {"weight": 0.2, "threshold": 1.5},
                "quick_ratio": {"weight": 0.2, "threshold": 1.0},
                "return_on_equity": {"weight": 0.15, "threshold": 0.15},
                "profit_margin": {"weight": 0.15, "threshold": 0.10}
            },
            "market_indicators": {
                "volatility": {"weight": 0.25, "threshold": 0.3},
                "beta": {"weight": 0.25, "threshold": 1.2},
                "market_cap": {"weight": 0.2, "threshold": 1000000000},
                "pe_ratio": {"weight": 0.15, "threshold": 25},
                "dividend_yield": {"weight": 0.15, "threshold": 0.05}
            },
            "operational_indicators": {
                "revenue_growth": {"weight": 0.3, "threshold": 0.1},
                "operating_margin": {"weight": 0.25, "threshold": 0.15},
                "asset_turnover": {"weight": 0.2, "threshold": 1.0},
                "inventory_turnover": {"weight": 0.15, "threshold": 5.0},
                "days_sales_outstanding": {"weight": 0.1, "threshold": 45}
            }
        }
    
    def load_models(self):
        """Load ML models (with fallback to basic models if custom models not available)"""
        try:
            # Try to load custom sentiment model
            if os.path.exists(self.model_paths["sentiment"]):
                self.sentiment_model = pipeline(
                    "sentiment-analysis",
                    model=self.model_paths["sentiment"],
                    tokenizer=self.model_paths["sentiment"]
                )
            else:
                # Fallback to basic sentiment model
                self.sentiment_model = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
            
            # Try to load custom summarizer
            if os.path.exists(self.model_paths["summarizer"]):
                self.summarizer = pipeline(
                    "summarization",
                    model=self.model_paths["summarizer"],
                    tokenizer=self.model_paths["summarizer"]
                )
            else:
                # Fallback to basic summarizer
                self.summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
            
            # Try to load custom classifier
            if os.path.exists(self.model_paths["classifier"]):
                self.classifier = pipeline(
                    "text-classification",
                    model=self.model_paths["classifier"],
                    tokenizer=self.model_paths["classifier"]
                )
            else:
                # Fallback to basic classifier
                self.classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")
                
        except Exception as e:
            print(f"Warning: Could not load custom models: {e}")
            # Use basic models as fallback
            self.sentiment_model = pipeline("sentiment-analysis")
            self.summarizer = pipeline("summarization")
            self.classifier = pipeline("text-classification")
    
    def predict_risk(self, file_path: str) -> Dict[str, Any]:
        """
        Enhanced risk prediction with multiple analysis layers
        """
        try:
            # Load models if not already loaded
            if self.sentiment_model is None:
                self.load_models()
            
            # Process the file
            processed_data = self.file_processor.process_file(file_path)
            
            if processed_data["file_type"] == "csv":
                return self._predict_from_financial_data(processed_data["data"])
            elif processed_data["file_type"] == "txt":
                return self._predict_from_text_data(processed_data["data"])
            else:
                return self._predict_generic(processed_data)
                
        except Exception as e:
            raise Exception(f"Enhanced risk prediction failed: {str(e)}")
    
    def _predict_from_financial_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Enhanced prediction from financial data"""
        try:
            # Calculate comprehensive risk indicators
            risk_indicators = self._calculate_financial_risk_indicators(df)
            
            # Perform sentiment analysis on text columns
            text_sentiment = self._analyze_text_sentiment(df)
            
            # Calculate market risk indicators
            market_risk = self._calculate_market_risk_indicators(df)
            
            # Calculate operational risk indicators
            operational_risk = self._calculate_operational_risk_indicators(df)
            
            # Combine all risk factors
            overall_risk_score = self._calculate_weighted_risk_score(
                risk_indicators, text_sentiment, market_risk, operational_risk
            )
            
            # Calculate confidence based on data quality and model performance
            confidence = self._calculate_prediction_confidence(df, risk_indicators)
            
            return {
                "risk_score": overall_risk_score,
                "confidence": confidence,
                "prediction_data": {
                    "financial_risk_indicators": risk_indicators,
                    "text_sentiment": text_sentiment,
                    "market_risk_indicators": market_risk,
                    "operational_risk_indicators": operational_risk,
                    "risk_breakdown": self._get_risk_breakdown(risk_indicators, text_sentiment, market_risk, operational_risk),
                    "data_quality": self._assess_data_quality(df),
                    "risk_factors": self._identify_enhanced_risk_factors(df, risk_indicators),
                    "recommendations": self._generate_risk_recommendations(overall_risk_score, risk_indicators)
                }
            }
            
        except Exception as e:
            raise Exception(f"Financial data prediction failed: {str(e)}")
    
    def _predict_from_text_data(self, text: str) -> Dict[str, Any]:
        """Enhanced prediction from text data"""
        try:
            # Advanced sentiment analysis
            sentiment_analysis = self._perform_advanced_sentiment_analysis(text)
            
            # Text summarization for key insights
            summary_analysis = self._analyze_text_summary(text)
            
            # Risk keyword analysis
            risk_keywords = self._extract_enhanced_risk_keywords(text)
            
            # Topic modeling for risk themes
            risk_themes = self._identify_risk_themes(text)
            
            # Calculate text-based risk score
            text_risk_score = self._calculate_text_risk_score(
                sentiment_analysis, risk_keywords, risk_themes
            )
            
            # Calculate confidence
            confidence = self._calculate_text_confidence(text, sentiment_analysis)
            
            return {
                "risk_score": text_risk_score,
                "confidence": confidence,
                "prediction_data": {
                    "sentiment_analysis": sentiment_analysis,
                    "summary_analysis": summary_analysis,
                    "risk_keywords": risk_keywords,
                    "risk_themes": risk_themes,
                    "text_analysis": self._analyze_text_content(text),
                    "risk_indicators": self._extract_text_risk_indicators(text),
                    "recommendations": self._generate_text_recommendations(text_risk_score, sentiment_analysis)
                }
            }
            
        except Exception as e:
            raise Exception(f"Text prediction failed: {str(e)}")
    
    def _calculate_financial_risk_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate comprehensive financial risk indicators"""
        indicators = {}
        
        # Get numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_lower = col.lower()
            
            # Debt-related indicators
            if any(word in col_lower for word in ['debt', 'liability', 'loan']):
                indicators[f"{col}_risk"] = self._calculate_debt_risk(df[col])
            
            # Revenue/Income indicators
            elif any(word in col_lower for word in ['revenue', 'income', 'sales']):
                indicators[f"{col}_risk"] = self._calculate_revenue_risk(df[col])
            
            # Ratio indicators
            elif 'ratio' in col_lower:
                indicators[f"{col}_risk"] = self._calculate_ratio_risk(df[col])
            
            # Asset indicators
            elif any(word in col_lower for word in ['asset', 'equity', 'capital']):
                indicators[f"{col}_risk"] = self._calculate_asset_risk(df[col])
            
            # Cash flow indicators
            elif any(word in col_lower for word in ['cash', 'flow', 'liquidity']):
                indicators[f"{col}_risk"] = self._calculate_cash_flow_risk(df[col])
        
        return indicators
    
    def _analyze_text_sentiment(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze sentiment in text columns"""
        sentiment_results = {}
        
        # Find text columns
        text_cols = df.select_dtypes(include=['object']).columns
        
        for col in text_cols:
            try:
                # Sample text for analysis (first non-null value)
                sample_text = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else ""
                
                if sample_text and len(sample_text) > 10:
                    # Perform sentiment analysis
                    sentiment_result = self.sentiment_model(sample_text[:500])  # Limit text length
                    sentiment_results[col] = {
                        "sentiment": sentiment_result[0]["label"],
                        "confidence": sentiment_result[0]["score"],
                        "sample_text": sample_text[:100] + "..." if len(sample_text) > 100 else sample_text
                    }
            except Exception as e:
                sentiment_results[col] = {"error": str(e)}
        
        return sentiment_results
    
    def _calculate_market_risk_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate market-related risk indicators"""
        market_risk = {}
        
        # This would typically use market data
        # For now, we'll calculate basic volatility and trend indicators
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if len(df[col].dropna()) > 1:
                # Calculate volatility
                volatility = df[col].std() / df[col].mean() if df[col].mean() != 0 else 0
                market_risk[f"{col}_volatility"] = min(1.0, volatility)
                
                # Calculate trend (positive or negative)
                if len(df[col].dropna()) > 2:
                    trend = (df[col].iloc[-1] - df[col].iloc[0]) / df[col].iloc[0] if df[col].iloc[0] != 0 else 0
                    market_risk[f"{col}_trend"] = max(0, -trend)  # Negative trend = higher risk
        
        return market_risk
    
    def _calculate_operational_risk_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate operational risk indicators"""
        operational_risk = {}
        
        # Calculate operational metrics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if len(df[col].dropna()) > 1:
                # Calculate consistency (lower consistency = higher risk)
                consistency = 1 - (df[col].std() / df[col].mean()) if df[col].mean() != 0 else 0
                operational_risk[f"{col}_consistency"] = max(0, 1 - consistency)
        
        return operational_risk
    
    def _calculate_weighted_risk_score(self, financial_risk: Dict, text_sentiment: Dict, 
                                     market_risk: Dict, operational_risk: Dict) -> float:
        """Calculate weighted overall risk score"""
        weights = {
            "financial": 0.4,
            "text_sentiment": 0.2,
            "market": 0.25,
            "operational": 0.15
        }
        
        # Calculate component scores
        financial_score = np.mean(list(financial_risk.values())) if financial_risk else 0.5
        text_score = self._calculate_text_sentiment_score(text_sentiment)
        market_score = np.mean(list(market_risk.values())) if market_risk else 0.5
        operational_score = np.mean(list(operational_risk.values())) if operational_risk else 0.5
        
        # Weighted average
        overall_score = (
            weights["financial"] * financial_score +
            weights["text_sentiment"] * text_score +
            weights["market"] * market_score +
            weights["operational"] * operational_score
        )
        
        return round(overall_score, 3)
    
    def _calculate_text_sentiment_score(self, sentiment_data: Dict) -> float:
        """Calculate risk score from text sentiment"""
        if not sentiment_data:
            return 0.5
        
        sentiment_scores = []
        for col_data in sentiment_data.values():
            if isinstance(col_data, dict) and "sentiment" in col_data:
                if col_data["sentiment"] == "NEGATIVE":
                    sentiment_scores.append(0.8)  # High risk for negative sentiment
                elif col_data["sentiment"] == "POSITIVE":
                    sentiment_scores.append(0.2)  # Low risk for positive sentiment
                else:
                    sentiment_scores.append(0.5)  # Neutral
        
        return np.mean(sentiment_scores) if sentiment_scores else 0.5
    
    def _perform_advanced_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Perform advanced sentiment analysis"""
        try:
            # Basic sentiment analysis
            sentiment_result = self.sentiment_model(text[:500])
            
            # Extract sentiment indicators
            positive_words = ['good', 'great', 'excellent', 'positive', 'profit', 'growth', 'increase', 'success', 'strong']
            negative_words = ['bad', 'poor', 'negative', 'loss', 'decline', 'decrease', 'risk', 'failure', 'debt', 'weak']
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            return {
                "overall_sentiment": sentiment_result[0]["label"],
                "sentiment_confidence": sentiment_result[0]["score"],
                "positive_indicators": positive_count,
                "negative_indicators": negative_count,
                "sentiment_ratio": positive_count / (positive_count + negative_count) if (positive_count + negative_count) > 0 else 0.5
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_text_summary(self, text: str) -> Dict[str, Any]:
        """Analyze text summary for risk insights"""
        try:
            # Generate summary
            summary = self.summarizer(text[:1000], max_length=150, min_length=50, do_sample=False)
            
            # Analyze summary sentiment
            summary_sentiment = self.sentiment_model(summary[0]["summary_text"])
            
            return {
                "summary": summary[0]["summary_text"],
                "summary_sentiment": summary_sentiment[0]["label"],
                "summary_confidence": summary_sentiment[0]["score"],
                "summary_length": len(summary[0]["summary_text"])
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_enhanced_risk_keywords(self, text: str) -> Dict[str, int]:
        """Extract enhanced risk keywords with categories"""
        risk_categories = {
            "financial_risk": ['debt', 'loss', 'bankruptcy', 'default', 'liquidation'],
            "operational_risk": ['failure', 'breakdown', 'disruption', 'downtime', 'error'],
            "market_risk": ['volatility', 'decline', 'crash', 'bear', 'recession'],
            "regulatory_risk": ['regulation', 'compliance', 'penalty', 'investigation', 'lawsuit'],
            "strategic_risk": ['competition', 'disruption', 'innovation', 'obsolescence']
        }
        
        text_lower = text.lower()
        enhanced_keywords = {}
        
        for category, keywords in risk_categories.items():
            category_count = 0
            for keyword in keywords:
                count = text_lower.count(keyword)
                if count > 0:
                    enhanced_keywords[f"{category}_{keyword}"] = count
                    category_count += count
            
            if category_count > 0:
                enhanced_keywords[f"{category}_total"] = category_count
        
        return enhanced_keywords
    
    def _identify_risk_themes(self, text: str) -> Dict[str, float]:
        """Identify risk themes in text"""
        themes = {
            "financial_distress": 0.0,
            "operational_issues": 0.0,
            "market_volatility": 0.0,
            "regulatory_concerns": 0.0,
            "strategic_challenges": 0.0
        }
        
        text_lower = text.lower()
        
        # Financial distress indicators
        financial_words = ['debt', 'loss', 'bankruptcy', 'default', 'liquidation', 'insolvency']
        themes["financial_distress"] = sum(text_lower.count(word) for word in financial_words) / len(text.split())
        
        # Operational issues
        operational_words = ['failure', 'breakdown', 'disruption', 'downtime', 'error', 'defect']
        themes["operational_issues"] = sum(text_lower.count(word) for word in operational_words) / len(text.split())
        
        # Market volatility
        market_words = ['volatility', 'decline', 'crash', 'bear', 'recession', 'uncertainty']
        themes["market_volatility"] = sum(text_lower.count(word) for word in market_words) / len(text.split())
        
        # Regulatory concerns
        regulatory_words = ['regulation', 'compliance', 'penalty', 'investigation', 'lawsuit']
        themes["regulatory_concerns"] = sum(text_lower.count(word) for word in regulatory_words) / len(text.split())
        
        # Strategic challenges
        strategic_words = ['competition', 'disruption', 'innovation', 'obsolescence', 'challenge']
        themes["strategic_challenges"] = sum(text_lower.count(word) for word in strategic_words) / len(text.split())
        
        return themes
    
    def _calculate_text_risk_score(self, sentiment_analysis: Dict, risk_keywords: Dict, risk_themes: Dict) -> float:
        """Calculate comprehensive text risk score"""
        # Sentiment component (30%)
        sentiment_score = 1 - sentiment_analysis.get("sentiment_ratio", 0.5)
        
        # Keyword component (40%)
        total_keywords = sum(risk_keywords.values())
        keyword_score = min(1.0, total_keywords / 20)  # Normalize to 0-1
        
        # Theme component (30%)
        theme_score = np.mean(list(risk_themes.values())) * 1000  # Scale up small values
        
        # Weighted combination
        overall_score = 0.3 * sentiment_score + 0.4 * keyword_score + 0.3 * theme_score
        
        return round(overall_score, 3)
    
    def _calculate_prediction_confidence(self, df: pd.DataFrame, risk_indicators: Dict) -> float:
        """Calculate confidence in prediction"""
        # Data quality factors
        data_completeness = 1 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))
        data_volume = min(1.0, len(df) / 1000)
        
        # Model confidence factors
        indicator_count = len(risk_indicators)
        indicator_confidence = min(1.0, indicator_count / 10)
        
        # Overall confidence
        confidence = (data_completeness + data_volume + indicator_confidence) / 3
        
        return round(confidence, 3)
    
    def _calculate_text_confidence(self, text: str, sentiment_analysis: Dict) -> float:
        """Calculate confidence in text-based prediction"""
        # Text length factor
        word_count = len(text.split())
        length_confidence = min(1.0, word_count / 1000)
        
        # Sentiment confidence
        sentiment_confidence = sentiment_analysis.get("sentiment_confidence", 0.5)
        
        # Overall confidence
        confidence = (length_confidence + sentiment_confidence) / 2
        
        return round(confidence, 3)
    
    def _get_risk_breakdown(self, financial_risk: Dict, text_sentiment: Dict, 
                           market_risk: Dict, operational_risk: Dict) -> Dict[str, float]:
        """Get detailed risk breakdown"""
        return {
            "financial_risk": np.mean(list(financial_risk.values())) if financial_risk else 0.5,
            "sentiment_risk": self._calculate_text_sentiment_score(text_sentiment),
            "market_risk": np.mean(list(market_risk.values())) if market_risk else 0.5,
            "operational_risk": np.mean(list(operational_risk.values())) if operational_risk else 0.5
        }
    
    def _identify_enhanced_risk_factors(self, df: pd.DataFrame, risk_indicators: Dict) -> List[str]:
        """Identify enhanced risk factors"""
        risk_factors = []
        
        # Data quality issues
        missing_cols = df.columns[df.isnull().sum() > 0]
        if len(missing_cols) > 0:
            risk_factors.append(f"Missing data in {len(missing_cols)} columns")
        
        # High risk indicators
        high_risk_indicators = [k for k, v in risk_indicators.items() if v > 0.7]
        if high_risk_indicators:
            risk_factors.append(f"High risk detected in: {', '.join(high_risk_indicators[:3])}")
        
        # Volatility issues
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].std() > df[col].mean() * 2:
                risk_factors.append(f"High volatility detected in {col}")
        
        return risk_factors
    
    def _generate_risk_recommendations(self, risk_score: float, risk_indicators: Dict) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        if risk_score > 0.7:
            recommendations.append("🔴 HIGH RISK: Immediate action required")
            recommendations.append("Consider diversifying investments")
            recommendations.append("Review financial controls and procedures")
        elif risk_score > 0.5:
            recommendations.append("🟡 MEDIUM RISK: Monitor closely")
            recommendations.append("Implement risk mitigation strategies")
            recommendations.append("Regular risk assessments recommended")
        else:
            recommendations.append("🟢 LOW RISK: Standard monitoring")
            recommendations.append("Continue current risk management practices")
        
        # Specific recommendations based on indicators
        high_risk_indicators = [k for k, v in risk_indicators.items() if v > 0.6]
        if high_risk_indicators:
            recommendations.append(f"Focus on: {', '.join(high_risk_indicators[:3])}")
        
        return recommendations
    
    def _generate_text_recommendations(self, risk_score: float, sentiment_analysis: Dict) -> List[str]:
        """Generate recommendations based on text analysis"""
        recommendations = []
        
        if risk_score > 0.7:
            recommendations.append("🔴 High risk detected in text analysis")
            recommendations.append("Review communication strategies")
            recommendations.append("Consider external risk assessment")
        elif risk_score > 0.5:
            recommendations.append("🟡 Moderate risk in communications")
            recommendations.append("Monitor public sentiment")
            recommendations.append("Review messaging approach")
        else:
            recommendations.append("🟢 Low risk in text communications")
            recommendations.append("Continue current communication strategy")
        
        return recommendations
    
    # Helper methods (reused from original ML predictor)
    def _calculate_debt_risk(self, debt_series: pd.Series) -> float:
        if debt_series.isnull().all():
            return 0.5
        avg_debt = debt_series.mean()
        debt_volatility = debt_series.std()
        risk = min(1.0, (avg_debt / 1000000 + debt_volatility / 100000) / 2)
        return round(risk, 3)
    
    def _calculate_revenue_risk(self, revenue_series: pd.Series) -> float:
        if revenue_series.isnull().all():
            return 0.5
        if len(revenue_series) > 1:
            revenue_change = (revenue_series.iloc[-1] - revenue_series.iloc[0]) / revenue_series.iloc[0]
            risk = max(0.0, min(1.0, 0.5 - revenue_change))
        else:
            risk = 0.5
        return round(risk, 3)
    
    def _calculate_ratio_risk(self, ratio_series: pd.Series) -> float:
        if ratio_series.isnull().all():
            return 0.5
        mean_ratio = ratio_series.mean()
        std_ratio = ratio_series.std()
        risk = min(1.0, std_ratio / (abs(mean_ratio) + 1e-6))
        return round(risk, 3)
    
    def _calculate_asset_risk(self, asset_series: pd.Series) -> float:
        if asset_series.isnull().all():
            return 0.5
        asset_volatility = asset_series.std() / asset_series.mean() if asset_series.mean() != 0 else 0
        return round(min(1.0, asset_volatility), 3)
    
    def _calculate_cash_flow_risk(self, cash_series: pd.Series) -> float:
        if cash_series.isnull().all():
            return 0.5
        negative_cash_flow = (cash_series < 0).sum() / len(cash_series)
        return round(negative_cash_flow, 3)
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        return {
            "completeness": 1 - (df.isnull().sum().sum() / (len(df) * len(df.columns))),
            "consistency": self._check_data_consistency(df),
            "timeliness": "unknown"
        }
    
    def _check_data_consistency(self, df: pd.DataFrame) -> float:
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
    
    def _analyze_text_content(self, text: str) -> Dict[str, Any]:
        return {
            "word_count": len(text.split()),
            "sentence_count": len(text.split('.')),
            "complexity_score": self._calculate_text_complexity(text)
        }
    
    def _calculate_text_complexity(self, text: str) -> float:
        words = text.split()
        if not words:
            return 0.0
        avg_word_length = np.mean([len(word) for word in words])
        unique_word_ratio = len(set(words)) / len(words)
        complexity = (avg_word_length + unique_word_ratio) / 2
        return round(complexity, 3)
    
    def _extract_text_risk_indicators(self, text: str) -> Dict[str, Any]:
        return {
            "risk_keyword_density": len(self._extract_enhanced_risk_keywords(text)) / len(text.split()) * 1000,
            "sentiment_indicators": self._perform_advanced_sentiment_analysis(text)
        }
    
    def _predict_generic(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "risk_score": 0.5,
            "confidence": 0.1,
            "prediction_data": {
                "message": "Limited analysis available for this file type",
                "file_type": data.get("file_type", "unknown")
            }
        } 