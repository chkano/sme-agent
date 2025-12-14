"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str  # "sme" or "lender"


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    role: str
    
    class Config:
        from_attributes = True


# SME Schemas
class SMECreate(BaseModel):
    business_name: str
    industry: Optional[str] = None
    registration_number: Optional[str] = None


class SMEResponse(BaseModel):
    id: int
    user_id: int
    business_name: str
    industry: Optional[str]
    
    class Config:
        from_attributes = True


# Transaction Schemas
class TransactionCreate(BaseModel):
    transaction_date: datetime
    amount: float
    transaction_type: str
    category: Optional[str] = None
    description: Optional[str] = None
    source: str


class TransactionResponse(BaseModel):
    id: int
    sme_id: int
    transaction_date: datetime
    amount: float
    transaction_type: str
    category: Optional[str]
    
    class Config:
        from_attributes = True


# AgentQL Schema
class AgentQLRequest(BaseModel):
    query: str
    sme_id: int
    inputs: Optional[Dict[str, Any]] = None


# API Response Schemas
class FinancialHealthResponse(BaseModel):
    fhi_score: float
    metrics: Dict[str, Any]
    risk_flags: List[Dict[str, Any]]
    explanation: Optional[str] = None
    recommendations: Optional[List[str]] = None


class CashflowForecastResponse(BaseModel):
    forecast_days: int
    forecast: Dict[str, Dict[str, float]]
    stress_scenarios: Dict[str, Any]
    liquidity_risk_score: float
    forecast_summary: Dict[str, float]


class CreditScoreResponse(BaseModel):
    score: float
    calculation_date: datetime
    risk_factors: List[Dict[str, Any]]
    explanation: str
    recommendations: List[str]


class RiskAlertResponse(BaseModel):
    id: int
    sme_id: int
    alert_type: str
    severity: str
    message: str
    detected_at: datetime
    is_resolved: bool
    
    class Config:
        from_attributes = True


# Document Upload
class DocumentUploadResponse(BaseModel):
    document_id: int
    s3_key: str
    presigned_url: Optional[str] = None
