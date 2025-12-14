"""
Forecasting Agent - Predicts short-term cash flow and assesses liquidity risk
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import Transaction, CashflowForecast
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler


class ForecastingAgent:
    """Forecasts cash flow and liquidity risk"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def execute(self, sme_id: int, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute forecasting agent
        Predicts cash flow for next 30 days and simulates stress scenarios
        """
        # Get historical transaction data
        days_back = inputs.get("days_back", 90) if inputs else 90
        forecast_days = inputs.get("forecast_days", 30) if inputs else 30
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        transactions = self.db.query(Transaction).filter(
            and_(
                Transaction.sme_id == sme_id,
                Transaction.transaction_date >= cutoff_date
            )
        ).order_by(Transaction.transaction_date).all()
        
        if not transactions:
            return {
                "status": "insufficient_data",
                "forecast": None,
                "message": "Not enough transaction data for forecasting"
            }
        
        # Prepare time series data
        df = self._prepare_time_series(transactions)
        
        # Generate forecast
        forecast = self._generate_forecast(df, forecast_days)
        
        # Simulate stress scenarios
        stress_scenarios = self._simulate_stress_scenarios(df, forecast)
        
        # Calculate liquidity risk score
        liquidity_risk = self._calculate_liquidity_risk(forecast, stress_scenarios)
        
        # Store forecasts in database
        forecast_records = []
        for date, amount in forecast.items():
            forecast_record = CashflowForecast(
                sme_id=sme_id,
                forecast_date=date,
                predicted_amount=amount["predicted"],
                confidence_interval_lower=amount.get("lower"),
                confidence_interval_upper=amount.get("upper"),
                created_at=datetime.utcnow()
            )
            self.db.add(forecast_record)
            forecast_records.append(forecast_record)
        
        self.db.commit()
        
        return {
            "status": "success",
            "forecast_days": forecast_days,
            "forecast": {str(k): v for k, v in forecast.items()},
            "stress_scenarios": stress_scenarios,
            "liquidity_risk_score": liquidity_risk,
            "forecast_summary": {
                "total_predicted_inflow": sum(v["predicted"] for v in forecast.values() if v["predicted"] > 0),
                "total_predicted_outflow": abs(sum(v["predicted"] for v in forecast.values() if v["predicted"] < 0)),
                "predicted_net_cashflow": sum(v["predicted"] for v in forecast.values())
            }
        }
    
    def _prepare_time_series(self, transactions: List[Transaction]) -> pd.DataFrame:
        """Prepare daily cash flow time series"""
        df = pd.DataFrame([{
            "date": tx.transaction_date.date(),
            "amount": tx.amount if tx.transaction_type == "income" else -tx.amount
        } for tx in transactions])
        
        # Group by date
        daily_df = df.groupby("date")["amount"].sum().reset_index()
        daily_df.columns = ["date", "cashflow"]
        
        # Fill missing dates with 0
        date_range = pd.date_range(
            start=daily_df["date"].min(),
            end=daily_df["date"].max(),
            freq="D"
        )
        full_df = pd.DataFrame({"date": date_range.date})
        daily_df = full_df.merge(daily_df, on="date", how="left").fillna(0)
        
        # Add features
        daily_df["day_of_week"] = pd.to_datetime(daily_df["date"]).dt.dayofweek
        daily_df["day_of_month"] = pd.to_datetime(daily_df["date"]).dt.day
        daily_df["month"] = pd.to_datetime(daily_df["date"]).dt.month
        
        return daily_df
    
    def _generate_forecast(self, df: pd.DataFrame, forecast_days: int) -> Dict[datetime, Dict[str, float]]:
        """Generate cash flow forecast using time series analysis"""
        # Simple moving average with trend
        window = min(30, len(df) // 2)
        
        df["ma"] = df["cashflow"].rolling(window=window, center=False).mean()
        df["trend"] = df["cashflow"].rolling(window=window, center=False).mean().diff()
        
        # Get last values
        last_ma = df["ma"].iloc[-1] if not df["ma"].isna().iloc[-1] else df["cashflow"].mean()
        last_trend = df["trend"].iloc[-1] if not df["trend"].isna().iloc[-1] else 0
        last_std = df["cashflow"].tail(window).std()
        
        # Generate forecast
        forecast = {}
        start_date = datetime.utcnow().date()
        
        for i in range(forecast_days):
            forecast_date = start_date + timedelta(days=i)
            
            # Simple forecast: moving average + trend
            predicted = last_ma + (last_trend * i)
            
            # Confidence intervals (assuming normal distribution)
            lower = predicted - 1.96 * last_std  # 95% CI
            upper = predicted + 1.96 * last_std
            
            forecast[forecast_date] = {
                "predicted": float(predicted),
                "lower": float(lower),
                "upper": float(upper)
            }
        
        return forecast
    
    def _simulate_stress_scenarios(self, df: pd.DataFrame, forecast: Dict[datetime, Dict[str, float]]) -> Dict[str, Any]:
        """Simulate stress scenarios (revenue drop, expense increase)"""
        scenarios = {}
        
        # Baseline scenario (current forecast)
        baseline_net = sum(v["predicted"] for v in forecast.values())
        
        # Scenario 1: 20% revenue drop
        revenue_drop_net = baseline_net * 0.8
        scenarios["revenue_drop_20"] = {
            "net_cashflow": float(revenue_drop_net),
            "impact": "negative" if revenue_drop_net < 0 else "positive"
        }
        
        # Scenario 2: 30% expense increase
        expense_increase_net = baseline_net * 0.7
        scenarios["expense_increase_30"] = {
            "net_cashflow": float(expense_increase_net),
            "impact": "negative" if expense_increase_net < 0 else "positive"
        }
        
        # Scenario 3: Combined stress (20% revenue drop + 30% expense increase)
        combined_net = baseline_net * 0.5
        scenarios["combined_stress"] = {
            "net_cashflow": float(combined_net),
            "impact": "negative" if combined_net < 0 else "positive"
        }
        
        return scenarios
    
    def _calculate_liquidity_risk(self, forecast: Dict[datetime, Dict[str, float]], scenarios: Dict[str, Any]) -> float:
        """Calculate liquidity risk score (0-100, higher = more risk)"""
        # Base risk from forecast
        net_cashflow = sum(v["predicted"] for v in forecast.values())
        
        risk_score = 0.0
        
        # Negative cashflow = high risk
        if net_cashflow < 0:
            risk_score = min(100, abs(net_cashflow) / 1000 * 10)  # Scale based on deficit
        
        # Check stress scenarios
        if scenarios.get("combined_stress", {}).get("impact") == "negative":
            risk_score += 30
        
        if scenarios.get("revenue_drop_20", {}).get("impact") == "negative":
            risk_score += 15
        
        if scenarios.get("expense_increase_30", {}).get("impact") == "negative":
            risk_score += 15
        
        # Ensure score is between 0 and 100
        return min(100, max(0, risk_score))
