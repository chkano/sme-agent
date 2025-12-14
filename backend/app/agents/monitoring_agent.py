"""
Monitoring Agent - Continuously assesses SME financial behavior and stability
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.database import Transaction, FinancialHealthIndex, RiskAlert
import numpy as np
import pandas as pd


class MonitoringAgent:
    """Monitors financial health and detects anomalies"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def execute(self, sme_id: int, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute monitoring agent
        Calculates Financial Health Index and detects risk anomalies
        """
        # Get transaction data (last 90 days by default)
        days_back = inputs.get("days_back", 90) if inputs else 90
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.sme_id == sme_id,
                Transaction.transaction_date >= cutoff_date
            )
        ).all()
        
        if not transactions:
            return {
                "status": "insufficient_data",
                "fhi_score": None,
                "message": "Not enough transaction data for monitoring"
            }
        
        # Calculate metrics
        metrics = self._calculate_metrics(transactions)
        
        # Calculate Financial Health Index (0-100)
        fhi_score = self._calculate_fhi(metrics)
        
        # Detect anomalies and risk flags
        risk_flags = self._detect_risks(metrics, transactions)
        
        # Store FHI
        fhi_record = FinancialHealthIndex(
            sme_id=sme_id,
            fhi_score=fhi_score,
            calculation_date=datetime.utcnow(),
            metrics=metrics,
            risk_flags=risk_flags
        )
        self.db.add(fhi_record)
        
        # Create risk alerts if needed
        alerts_created = self._create_risk_alerts(sme_id, risk_flags)
        
        self.db.commit()
        
        return {
            "status": "success",
            "fhi_score": fhi_score,
            "metrics": metrics,
            "risk_flags": risk_flags,
            "alerts_created": alerts_created
        }
    
    def _calculate_metrics(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """Calculate financial metrics from transactions"""
        df = pd.DataFrame([{
            "date": tx.transaction_date,
            "amount": tx.amount,
            "type": tx.transaction_type
        } for tx in transactions])
        
        df['date'] = pd.to_datetime(df['date'])
        
        # Separate income and expenses
        income = df[df['type'] == 'income']['amount'].sum()
        expenses = df[df['type'] == 'expense']['amount'].sum()
        net_cashflow = income - expenses
        
        # Daily cash flow
        df['cashflow'] = df.apply(
            lambda row: row['amount'] if row['type'] == 'income' else -row['amount'],
            axis=1
        )
        daily_cashflow = df.groupby(df['date'].dt.date)['cashflow'].sum()
        
        # Volatility metrics
        cashflow_volatility = daily_cashflow.std() if len(daily_cashflow) > 1 else 0
        cashflow_mean = daily_cashflow.mean()
        cashflow_cv = (cashflow_volatility / cashflow_mean) if cashflow_mean != 0 else 0
        
        # Revenue consistency (coefficient of variation of daily income)
        daily_income = df[df['type'] == 'income'].groupby(df['date'].dt.date)['amount'].sum()
        revenue_consistency = 1 - min(daily_income.std() / daily_income.mean() if daily_income.mean() != 0 else 1, 1)
        
        # Expense ratios
        expense_ratio = expenses / income if income != 0 else 1
        
        # Number of transactions
        num_transactions = len(transactions)
        num_income = len(df[df['type'] == 'income'])
        num_expenses = len(df[df['type'] == 'expense'])
        
        return {
            "total_income": float(income),
            "total_expenses": float(expenses),
            "net_cashflow": float(net_cashflow),
            "cashflow_volatility": float(cashflow_volatility),
            "cashflow_coefficient_of_variation": float(cashflow_cv),
            "revenue_consistency": float(revenue_consistency),
            "expense_ratio": float(expense_ratio),
            "num_transactions": int(num_transactions),
            "num_income_transactions": int(num_income),
            "num_expense_transactions": int(num_expenses),
            "average_daily_cashflow": float(cashflow_mean),
            "period_days": len(daily_cashflow)
        }
    
    def _calculate_fhi(self, metrics: Dict[str, Any]) -> float:
        """Calculate Financial Health Index (0-100)"""
        score = 100.0
        
        # Penalize high expense ratio
        if metrics["expense_ratio"] > 0.9:
            score -= 20
        elif metrics["expense_ratio"] > 0.8:
            score -= 10
        
        # Penalize negative cashflow
        if metrics["net_cashflow"] < 0:
            score -= 30
        
        # Penalize high volatility
        if metrics["cashflow_coefficient_of_variation"] > 0.5:
            score -= 15
        elif metrics["cashflow_coefficient_of_variation"] > 0.3:
            score -= 8
        
        # Reward revenue consistency
        score += metrics["revenue_consistency"] * 10
        
        # Ensure score is between 0 and 100
        return max(0, min(100, score))
    
    def _detect_risks(self, metrics: Dict[str, Any], transactions: List[Transaction]) -> List[Dict[str, Any]]:
        """Detect financial risks and anomalies"""
        risk_flags = []
        
        # Negative cashflow risk
        if metrics["net_cashflow"] < 0:
            risk_flags.append({
                "type": "negative_cashflow",
                "severity": "high",
                "message": f"Negative cashflow detected: {metrics['net_cashflow']:.2f}"
            })
        
        # High expense ratio
        if metrics["expense_ratio"] > 0.9:
            risk_flags.append({
                "type": "high_expense_ratio",
                "severity": "medium",
                "message": f"Expense ratio is {metrics['expense_ratio']:.2%}"
            })
        
        # High volatility
        if metrics["cashflow_coefficient_of_variation"] > 0.5:
            risk_flags.append({
                "type": "high_volatility",
                "severity": "medium",
                "message": f"Cashflow volatility is high (CV: {metrics['cashflow_coefficient_of_variation']:.2f})"
            })
        
        # Anomaly detection (statistical outliers)
        amounts = [tx.amount for tx in transactions]
        if len(amounts) > 10:
            q1 = np.percentile(amounts, 25)
            q3 = np.percentile(amounts, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = [tx for tx in transactions if tx.amount < lower_bound or tx.amount > upper_bound]
            if outliers:
                risk_flags.append({
                    "type": "anomaly",
                    "severity": "low",
                    "message": f"Detected {len(outliers)} anomalous transactions"
                })
        
        return risk_flags
    
    def _create_risk_alerts(self, sme_id: int, risk_flags: List[Dict[str, Any]]) -> int:
        """Create risk alert records in database"""
        alerts_created = 0
        
        for flag in risk_flags:
            # Only create alerts for medium/high severity
            if flag["severity"] in ["medium", "high", "critical"]:
                alert = RiskAlert(
                    sme_id=sme_id,
                    alert_type=flag["type"],
                    severity=flag["severity"],
                    message=flag["message"],
                    detected_at=datetime.utcnow(),
                    alert_metadata=flag
                )
                self.db.add(alert)
                alerts_created += 1
        
        return alerts_created
