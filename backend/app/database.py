from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import settings

# Database engine
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "sme" or "lender"
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SME(Base):
    __tablename__ = "smes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    business_name = Column(String, nullable=False)
    industry = Column(String)
    registration_number = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    sme_id = Column(Integer, nullable=False, index=True)
    transaction_date = Column(DateTime, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)  # "income" or "expense"
    category = Column(String)
    description = Column(Text)
    source = Column(String)  # "bank_csv", "ecommerce", "ocr"
    raw_data = Column(JSON)  # Original data
    created_at = Column(DateTime, default=datetime.utcnow)


class FinancialHealthIndex(Base):
    __tablename__ = "financial_health_indices"
    
    id = Column(Integer, primary_key=True, index=True)
    sme_id = Column(Integer, nullable=False, index=True)
    fhi_score = Column(Float, nullable=False)  # 0-100
    calculation_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    metrics = Column(JSON)  # Detailed metrics
    risk_flags = Column(JSON)  # List of risk indicators


class CashflowForecast(Base):
    __tablename__ = "cashflow_forecasts"
    
    id = Column(Integer, primary_key=True, index=True)
    sme_id = Column(Integer, nullable=False, index=True)
    forecast_date = Column(DateTime, nullable=False)
    predicted_amount = Column(Float, nullable=False)
    confidence_interval_lower = Column(Float)
    confidence_interval_upper = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class CreditScore(Base):
    __tablename__ = "credit_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    sme_id = Column(Integer, nullable=False, index=True)
    score = Column(Float, nullable=False)  # 0-100
    calculation_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    risk_factors = Column(JSON)
    explanation = Column(Text)  # LLM-generated explanation


class RiskAlert(Base):
    __tablename__ = "risk_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    sme_id = Column(Integer, nullable=False, index=True)
    alert_type = Column(String, nullable=False)  # "liquidity", "anomaly", "decline"
    severity = Column(String, nullable=False)  # "low", "medium", "high", "critical"
    message = Column(Text, nullable=False)
    detected_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    is_resolved = Column(Boolean, default=False)
    alert_metadata = Column(JSON)  # Renamed from 'metadata' (SQLAlchemy reserved name)


class AgentExecution(Base):
    __tablename__ = "agent_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_type = Column(String, nullable=False)  # "extraction", "monitoring", "forecasting"
    sme_id = Column(Integer, nullable=False, index=True)
    agentql_query = Column(Text)  # Original AgentQL query
    inputs = Column(JSON)
    outputs = Column(JSON)
    status = Column(String, default="completed")  # "pending", "running", "completed", "failed"
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    error_message = Column(Text)


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    sme_id = Column(Integer, nullable=False, index=True)
    document_type = Column(String, nullable=False)  # "invoice", "receipt", "statement"
    s3_key = Column(String, nullable=False)  # S3 object key
    original_filename = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    document_metadata = Column(JSON)  # Renamed from 'metadata' (SQLAlchemy reserved name)


# Create all tables
def init_db():
    Base.metadata.create_all(bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
