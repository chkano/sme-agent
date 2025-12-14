# Agentic AI Credit Intelligence Platform

A comprehensive credit intelligence system designed to reduce information asymmetry in SME credit assessment using Agentic AI, alternative data, and explainable AI outputs.

## Architecture Overview

The system follows a **layered architecture** with the following components:

1. **Presentation Layer** - React frontend dashboards for SMEs and lenders
2. **Application & API Layer** - FastAPI backend with RESTful APIs
3. **Agentic Orchestration Layer** - Agent Controller and AgentQL for agent management
4. **Specialized Agent Layer** - Extraction, Monitoring, and Forecasting agents
5. **Intelligence & Reasoning Layer** - ML models and LLM-based reasoning/validation
6. **Data Layer** - PostgreSQL (Supabase) and AWS S3

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL via Supabase
- **Object Storage**: AWS S3
- **ML/LLM**: OpenAI GPT-4, XGBoost/LightGBM
- **Authentication**: JWT tokens

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query (React Query)
- **Routing**: React Router

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 18+
- Supabase account and project
- AWS account with S3 bucket
- OpenAI API key

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```

5. Configure your `.env` file:
```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
DATABASE_URL=postgresql://user:password@db.xxxxx.supabase.co:5432/postgres

# AWS S3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=credit-intelligence-storage

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# JWT
SECRET_KEY=your-secret-key-for-jwt-tokens
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

6. Initialize the database (creates tables):
```bash
python -c "from app.database import init_db; init_db()"
```

7. Run the FastAPI server:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Key Features

### Agentic AI System

- **Extraction Agent**: Processes bank CSVs, e-commerce data, and OCR documents
- **Monitoring Agent**: Continuously assesses financial health and detects anomalies
- **Forecasting Agent**: Predicts cash flow and liquidity risk

### Core APIs

- `POST /financial-health` - Get Financial Health Index (FHI) and risk analysis
- `POST /cashflow-forecast` - Get cash flow predictions for next 30 days
- `POST /credit-score` - Get credit readiness score with AI explanations
- `GET /risk-alerts` - View active risk alerts
- `POST /agentql/execute` - Execute AgentQL queries for custom workflows

### AgentQL

AgentQL is a domain-specific language for controlling agent execution:

```
QUERY credit_readiness
USING last_90_days_transactions
EXECUTE Extraction -> Monitoring -> Forecasting
RETURN score, risk_factors, explanation
```

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── agents/          # Agentic AI agents
│   │   │   ├── agent_controller.py
│   │   │   ├── agentql.py
│   │   │   ├── extraction_agent.py
│   │   │   ├── monitoring_agent.py
│   │   │   └── forecasting_agent.py
│   │   ├── intelligence/    # ML and LLM layers
│   │   │   ├── ml_scoring.py
│   │   │   ├── llm_reasoning.py
│   │   │   └── llm_validation.py
│   │   ├── storage/         # S3 integration
│   │   │   └── s3_client.py
│   │   ├── auth.py          # Authentication
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # Database models
│   │   ├── main.py          # FastAPI app
│   │   └── schemas.py       # Pydantic schemas
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── pages/           # React pages
│   │   ├── contexts/        # React contexts
│   │   ├── services/        # API clients
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
└── README.md
```

## Usage

1. **Register/Login**: Create an account as SME or Lender
2. **SME Profile**: SME users must create a profile
3. **Upload Data**: Upload bank statements, invoices, etc.
4. **View Insights**: Access Financial Health, Credit Score, and Risk Alerts
5. **Agent Execution**: Use AgentQL to run custom agent workflows

## Development

### Running Tests

```bash
# Backend tests (to be added)
cd backend
pytest

# Frontend tests (to be added)
cd frontend
npm test
```

### Database Migrations

The system uses SQLAlchemy ORM. For production, consider using Alembic for migrations.

## License

This project is part of an Independent Study research project.

## Contributing

This is a research prototype. For questions or contributions, please contact the project maintainer.
# sme-agent
