"""
ML Scoring Models - Generate quantitative indicators (Financial Strength Score, etc.)
"""
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from app.database import Transaction, FinancialHealthIndex, CashflowForecast
from sqlalchemy.orm import Session
from datetime import datetime, timedelta


class MLScoringModel:
    """Machine learning models for financial strength scoring"""
    
    def __init__(self, db: Session):
        self.db = db
        self.model = None
    
    def calculate_financial_strength_score(self, sme_id: int) -> Dict[str, Any]:
        """
        Calculate Financial Strength Score (0-100) using ML model
        Combines various financial indicators
        """
        # Extract features
        features = self._extract_features(sme_id)
        
        # Calculate score using rule-based approach (can be replaced with trained ML model)
        score = self._calculate_score(features)
        
        return {
            "score": score,
            "features": features,
            "calculation_date": datetime.utcnow().isoformat()
        }
    
    def _extract_features(self, sme_id: int) -> Dict[str, float]:
        """Extract features for scoring"""
        # Get recent transactions
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        transactions = self.db.query(Transaction).filter(
            Transaction.sme_id == sme_id,
            Transaction.transaction_date >= cutoff_date
        ).all()
        
        if not transactions:
            return {}
        
        df = pd.DataFrame([{
            "amount": tx.amount,
            "type": tx.transaction_type
        } for tx in transactions])
        
        income = df[df['type'] == 'income']['amount'].sum()
        expenses = df[df['type'] == 'expense']['amount'].sum()
        net_cashflow = income - expenses
        
        # Cashflow ratios
        cashflow_ratio = (net_cashflow / income) if income > 0 else -1
        
        # Volatility
        daily_cashflow = []
        for tx in transactions:
            daily_cashflow.append(tx.amount if tx.transaction_type == 'income' else -tx.amount)
        
        volatility = np.std(daily_cashflow) if len(daily_cashflow) > 1 else 0
        mean_cashflow = np.mean(daily_cashflow) if daily_cashflow else 0
        cv = (volatility / mean_cashflow) if mean_cashflow != 0 else 0
        
        # Get latest FHI
        latest_fhi = self.db.query(FinancialHealthIndex).filter(
            FinancialHealthIndex.sme_id == sme_id
        ).order_by(FinancialHealthIndex.calculation_date.desc()).first()
        
        fhi_score = latest_fhi.fhi_score if latest_fhi else 50.0
        
        # Get liquidity risk from latest forecast
        latest_forecast = self.db.query(CashflowForecast).filter(
            CashflowForecast.sme_id == sme_id
        ).order_by(CashflowForecast.created_at.desc()).limit(30).all()
        
        forecasted_net = sum(f.predicted_amount for f in latest_forecast) if latest_forecast else 0
        
        return {
            "total_income": float(income),
            "total_expenses": float(expenses),
            "net_cashflow": float(net_cashflow),
            "cashflow_ratio": float(cashflow_ratio),
            "volatility": float(volatility),
            "coefficient_of_variation": float(cv),
            "fhi_score": float(fhi_score),
            "forecasted_net_cashflow": float(forecasted_net),
            "transaction_count": len(transactions)
        }
    
    def _calculate_score(self, features: Dict[str, float]) -> float:
        """Calculate financial strength score from features"""
        if not features:
            return 0.0
        
        score = 50.0  # Base score
        
        # Cashflow ratio contribution (0-25 points)
        cashflow_ratio = features.get("cashflow_ratio", -1)
        if cashflow_ratio > 0.2:
            score += 25
        elif cashflow_ratio > 0.1:
            score += 20
        elif cashflow_ratio > 0:
            score += 10
        elif cashflow_ratio > -0.1:
            score += 5
        
        # FHI contribution (0-25 points)
        fhi_score = features.get("fhi_score", 50)
        score += (fhi_score / 100) * 25
        
        # Volatility penalty (0-15 points deduction)
        cv = features.get("coefficient_of_variation", 1)
        if cv > 0.5:
            score -= 15
        elif cv > 0.3:
            score -= 10
        elif cv > 0.2:
            score -= 5
        
        # Forecasted cashflow contribution (0-15 points)
        forecasted_net = features.get("forecasted_net_cashflow", 0)
        if forecasted_net > 10000:
            score += 15
        elif forecasted_net > 5000:
            score += 10
        elif forecasted_net > 0:
            score += 5
        
        # Ensure score is between 0 and 100
        return max(0, min(100, score))
