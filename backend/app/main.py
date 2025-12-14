"""
FastAPI Application - Main entry point
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.config import settings
from app.database import get_db, init_db, User, SME, RiskAlert, CreditScore, Document
from app.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_sme_user,
    get_password_hash,
    get_current_lender_user
)
from app.schemas import (
    Token,
    UserCreate,
    UserResponse,
    SMECreate,
    SMEResponse,
    FinancialHealthResponse,
    CashflowForecastResponse,
    CreditScoreResponse,
    RiskAlertResponse,
    AgentQLRequest,
    DocumentUploadResponse,
    LoginRequest
)
from app.agents import AgentController
from app.intelligence import MLScoringModel, LLMReasoning, LLMValidation
from app.storage.s3_client import s3_client

app = FastAPI(
    title="Agentic AI Credit Intelligence Platform",
    description="Credit intelligence system using agentic AI for SME credit assessment",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()


# ============ Authentication Endpoints ============

@app.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


from app.schemas import LoginRequest

@app.post("/auth/token", response_model=Token)
async def login_for_access_token(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# ============ SME Endpoints ============

@app.post("/smes", response_model=SMEResponse)
async def create_sme(
    sme_data: SMECreate,
    current_user: User = Depends(get_current_sme_user),
    db: Session = Depends(get_db)
):
    """Create or update SME profile"""
    # Check if SME profile exists
    sme = db.query(SME).filter(SME.user_id == current_user.id).first()
    
    if sme:
        # Update existing
        sme.business_name = sme_data.business_name
        sme.industry = sme_data.industry
        sme.registration_number = sme_data.registration_number
    else:
        # Create new
        sme = SME(
            user_id=current_user.id,
            business_name=sme_data.business_name,
            industry=sme_data.industry,
            registration_number=sme_data.registration_number
        )
        db.add(sme)
    
    db.commit()
    db.refresh(sme)
    return sme


@app.get("/smes/me", response_model=SMEResponse)
async def get_my_sme(
    current_user: User = Depends(get_current_sme_user),
    db: Session = Depends(get_db)
):
    """Get current user's SME profile"""
    sme = db.query(SME).filter(SME.user_id == current_user.id).first()
    if not sme:
        raise HTTPException(status_code=404, detail="SME profile not found")
    return sme


# ============ Core Credit Intelligence APIs ============

@app.post("/financial-health", response_model=FinancialHealthResponse)
async def get_financial_health(
    sme_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get financial health analysis
    Uses Monitoring Agent to calculate FHI and detect risks
    """
    # Determine SME ID (SME users use their own, lenders specify)
    if current_user.role == "sme":
        sme = db.query(SME).filter(SME.user_id == current_user.id).first()
        if not sme:
            raise HTTPException(status_code=404, detail="SME profile not found")
        sme_id = sme.id
    elif not sme_id:
        raise HTTPException(status_code=400, detail="sme_id required for lender users")
    
    # Execute monitoring agent
    agent_controller = AgentController(db)
    monitoring_result = await agent_controller.execute_agent(
        "monitoring",
        sme_id=sme_id,
        inputs={"days_back": 90}
    )
    
    # Generate explanation using LLM
    llm_reasoning = LLMReasoning()
    explanation = llm_reasoning.generate_explanation({
        "fhi_score": monitoring_result["fhi_score"]
    })
    
    # Generate recommendations
    recommendations = llm_reasoning.generate_recommendations(
        {"fhi_score": monitoring_result["fhi_score"]},
        monitoring_result.get("risk_flags", [])
    )
    
    return FinancialHealthResponse(
        fhi_score=monitoring_result["fhi_score"],
        metrics=monitoring_result.get("metrics", {}),
        risk_flags=monitoring_result.get("risk_flags", []),
        explanation=explanation,
        recommendations=recommendations
    )


@app.post("/cashflow-forecast", response_model=CashflowForecastResponse)
async def get_cashflow_forecast(
    forecast_days: int = 30,
    sme_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get cash flow forecast
    Uses Forecasting Agent to predict liquidity risk
    """
    # Determine SME ID
    if current_user.role == "sme":
        sme = db.query(SME).filter(SME.user_id == current_user.id).first()
        if not sme:
            raise HTTPException(status_code=404, detail="SME profile not found")
        sme_id = sme.id
    elif not sme_id:
        raise HTTPException(status_code=400, detail="sme_id required for lender users")
    
    # Execute forecasting agent
    agent_controller = AgentController(db)
    forecast_result = await agent_controller.execute_agent(
        "forecasting",
        sme_id=sme_id,
        inputs={"forecast_days": forecast_days, "days_back": 90}
    )
    
    return CashflowForecastResponse(**forecast_result)


@app.post("/credit-score", response_model=CreditScoreResponse)
async def get_credit_score(
    sme_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get credit score with explainable AI
    Combines ML scoring with LLM reasoning
    """
    # Determine SME ID
    if current_user.role == "sme":
        sme = db.query(SME).filter(SME.user_id == current_user.id).first()
        if not sme:
            raise HTTPException(status_code=404, detail="SME profile not found")
        sme_id = sme.id
    elif not sme_id:
        raise HTTPException(status_code=400, detail="sme_id required for lender users")
    
    # Calculate financial strength score
    ml_model = MLScoringModel(db)
    score_result = ml_model.calculate_financial_strength_score(sme_id)
    
    # Get risk factors from monitoring
    agent_controller = AgentController(db)
    monitoring_result = await agent_controller.execute_agent("monitoring", sme_id=sme_id)
    risk_factors = monitoring_result.get("risk_flags", [])
    
    # Generate explanation and recommendations
    llm_reasoning = LLMReasoning()
    explanation = llm_reasoning.generate_explanation(score_result)
    recommendations = llm_reasoning.generate_recommendations(
        {"financial_strength_score": score_result["score"]},
        risk_factors
    )
    
    # Validate explanation
    llm_validation = LLMValidation()
    validation_result = llm_validation.validate_explanation(explanation, score_result)
    
    # If validation fails, regenerate
    if not validation_result.get("is_valid", True):
        explanation = f"{explanation} [Note: This assessment has been flagged for review]"
    
    # Store credit score
    credit_score = CreditScore(
        sme_id=sme_id,
        score=score_result["score"],
        calculation_date=datetime.utcnow(),
        risk_factors=risk_factors,
        explanation=explanation
    )
    db.add(credit_score)
    db.commit()
    
    return CreditScoreResponse(
        score=score_result["score"],
        calculation_date=datetime.utcnow(),
        risk_factors=risk_factors,
        explanation=explanation,
        recommendations=recommendations
    )


@app.get("/risk-alerts", response_model=List[RiskAlertResponse])
async def get_risk_alerts(
    sme_id: Optional[int] = None,
    severity: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get risk alerts for SME"""
    # Determine SME ID
    if current_user.role == "sme":
        sme = db.query(SME).filter(SME.user_id == current_user.id).first()
        if not sme:
            raise HTTPException(status_code=404, detail="SME profile not found")
        sme_id = sme.id
    elif not sme_id:
        raise HTTPException(status_code=400, detail="sme_id required for lender users")
    
    query = db.query(RiskAlert).filter(RiskAlert.sme_id == sme_id)
    
    if severity:
        query = query.filter(RiskAlert.severity == severity)
    
    alerts = query.order_by(RiskAlert.detected_at.desc()).limit(50).all()
    return alerts


# ============ AgentQL Endpoint ============

@app.post("/agentql/execute")
async def execute_agentql(
    request: AgentQLRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute an AgentQL query"""
    # Verify SME ownership for SME users
    if current_user.role == "sme":
        sme = db.query(SME).filter(SME.user_id == current_user.id).first()
        if not sme or sme.id != request.sme_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    agent_controller = AgentController(db)
    result = await agent_controller.execute_query(
        agentql_query=request.query,
        sme_id=request.sme_id,
        inputs=request.inputs
    )
    
    return result


# ============ Document Upload Endpoint ============

@app.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = "invoice",
    sme_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a document to S3"""
    # Determine SME ID
    if current_user.role == "sme":
        sme = db.query(SME).filter(SME.user_id == current_user.id).first()
        if not sme:
            raise HTTPException(status_code=404, detail="SME profile not found")
        sme_id = sme.id
    elif not sme_id:
        raise HTTPException(status_code=400, detail="sme_id required for lender users")
    
    # Generate S3 key
    s3_key = s3_client.generate_key(sme_id, document_type, file.filename)
    
    # Upload to S3
    s3_client.upload_file(
        file.file,
        s3_key,
        content_type=file.content_type
    )
    
    # Create database record
    document = Document(
        sme_id=sme_id,
        document_type=document_type,
        s3_key=s3_key,
        original_filename=file.filename
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Generate presigned URL
    presigned_url = s3_client.generate_presigned_url(s3_key)
    
    return DocumentUploadResponse(
        document_id=document.id,
        s3_key=s3_key,
        presigned_url=presigned_url
    )


# ============ Health Check ============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "credit-intelligence-api"}
