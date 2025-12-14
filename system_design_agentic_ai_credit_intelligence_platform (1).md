## 1. Clean Layered Architecture Overview

The system is redesigned into **clear, bank-grade layers** to improve readability, scalability, and thesis defensibility. This architecture follows **separation of concerns** and aligns with **BFI risk, governance, and explainability requirements**.

---

## 2. Layered Architecture (Top → Bottom)

### Layer 1: Presentation Layer (User Interaction)
**Components**
- SME Web Dashboard
- Lender / Credit Officer Dashboard

**Responsibilities**
- Visualize financial health, credit readiness, and alerts
- Display explainable AI outputs
- Role-based access (SME vs Lender)

**Design Rationale**
- Transparency for SMEs
- Explainability and trust for lenders

---

### Layer 2: Application & API Layer
**Components**
- FastAPI Backend
- Authentication & Authorization
- Credit Intelligence APIs

**Key APIs**
- `/financial-health`
- `/cashflow-forecast`
- `/credit-score`
- `/risk-alerts`

**Design Rationale**
- Acts as system orchestrator
- Enables integration with banks, fintechs, and regulators
- Production-ready interface

---

### Layer 3: Agentic Orchestration Layer (Core Innovation)

This layer operationalizes **Agentic AI** and is the core contribution of the IS.

#### 3.1 Agent Controller
- Manages agent lifecycle
- Assigns tasks
- Controls execution order

#### 3.2 AgentQL (Control & Instruction Layer)
- Standardized agent instructions
- Prevents hallucination
- Enables auditability

**Example**
```
QUERY cashflow_forecast
USING last_90_days_transactions
RETURN forecast, liquidity_risk, explanation
```

---

### Layer 4: Specialized Agent Layer

#### Extraction Agent (Data Structuring)
- Ingests bank CSVs, e-commerce data, OCR documents
- Normalizes and categorizes transactions

#### Monitoring Agent (Financial Health)
- Tracks cash flow stability
- Detects anomalies and behavioral risk
- Generates Financial Health Index (FHI)

#### Forecasting Agent (Liquidity Risk)
- Predicts short-term cash flow
- Simulates stress scenarios

**Design Rationale**
- Mirrors functional SME finance team
- Enables continuous, autonomous monitoring

---

### Layer 5: Intelligence & Reasoning Layer

#### ML Scoring Models
- Financial Strength Score
- Probability-of-stress indicators
- Uses alternative + behavioral data

#### LLM – Reasoning & Explanation
- Converts scores into human-readable insights
- Generates actionable recommendations

#### LLM – Validation & Safety
- Cross-checks outputs
- Bias and sanity validation

**Design Rationale**
- Balances predictive power with explainability
- Supports regulatory acceptance

---

### Layer 6: Data Layer

#### Structured Data Store (PostgreSQL / Supabase)
- Time-series metrics
- Agent memory
- Audit logs

#### Unstructured Data Store (Object Storage)
- Invoices, receipts, OCR images

**Design Rationale**
- Compliance-friendly separation
- Scalable for real-world deployment

---

## 3. Clean Redrawn Architecture (Textual Diagram)

```
┌───────────────────────────────────────┐
│           Presentation Layer          │
│  SME Dashboard | Lender Dashboard     │
└───────────────────────────────────────┘
                │
┌───────────────────────────────────────┐
│        Application / API Layer        │
│     FastAPI | Auth | Credit APIs      │
└───────────────────────────────────────┘
                │
┌───────────────────────────────────────┐
│      Agentic Orchestration Layer      │
│   Agent Controller | AgentQL          │
└───────────────────────────────────────┘
                │
┌───────────────────────────────────────┐
│         Specialized Agent Layer       │
│ Extraction | Monitoring | Forecasting │
└───────────────────────────────────────┘
                │
┌───────────────────────────────────────┐
│     Intelligence & Reasoning Layer    │
│   ML Models | LLM Reasoning | Safety  │
└───────────────────────────────────────┘
                │
┌───────────────────────────────────────┐
│               Data Layer              │
│ PostgreSQL | Object Storage | Logs    │
└───────────────────────────────────────┘
```

---

## 4. Why This Architecture Is Strong for IS & Industry

- **Academically strong**: Clear agent autonomy + control (AgentQL)
- **Industry-aligned**: Mirrors real bank credit workflow
- **Explainable**: LLM reasoning + validation
- **Scalable**: MVP → Bank integration
- **Commercializable**: Fintech / SME SaaS ready

---

## 5. Positioning Statement (Use in Chapter 3)

> *The proposed system adopts a layered agentic architecture to reduce information asymmetry in SME credit assessment by continuously transforming alternative data into explainable, finance-ready intelligence.*


---

## 6. Chapter 3: System Design (IS Thesis Ready)

### 3.1 System Architecture Overview

This research proposes an **Agentic AI–based Credit Intelligence System** designed to reduce information asymmetry between Thai SMEs and financial institutions. The system adopts a **layered architecture** to ensure modularity, scalability, explainability, and regulatory readiness. Each layer encapsulates a distinct responsibility, enabling independent development and evaluation while supporting end-to-end credit intelligence generation.

The architecture is intentionally designed to mirror real-world credit assessment workflows in banking and financial institutions, while introducing **agent autonomy** for continuous financial monitoring and decision support.

---

### 3.2 Architectural Layers Description

#### 3.2.1 Presentation Layer

The Presentation Layer provides user interaction interfaces for two primary stakeholders: **SME owners** and **lender-side credit officers**. The SME dashboard focuses on financial health visualization, credit readiness indicators, and AI-generated recommendations. The lender dashboard presents summarized risk signals, financial strength scores, and explainable insights.

This layer is designed to enhance transparency and trust by allowing SMEs to understand how their financial behaviors affect credit decisions, while enabling lenders to assess risk efficiently.

---

#### 3.2.2 Application & API Layer

The Application Layer is implemented using FastAPI and serves as the central orchestration point of the system. It manages authentication, authorization, request routing, and communication between user interfaces and backend intelligence components.

Core APIs include financial health analysis, cash flow forecasting, credit scoring, and risk alert generation. This layer enables seamless integration with external systems such as banks, fintech platforms, or future open banking services.

---

#### 3.2.3 Agentic Orchestration Layer

The Agentic Orchestration Layer coordinates autonomous agents within the system. An **Agent Controller** manages agent lifecycle, task assignment, and execution sequencing. To ensure control and auditability, the system employs **AgentQL**, a structured instruction mechanism that standardizes how agents receive tasks and return outputs.

This layer is a key research contribution, demonstrating how agent autonomy can be governed to meet financial industry requirements for explainability and reliability.

---

#### 3.2.4 Specialized Agent Layer

The Specialized Agent Layer consists of autonomous agents, each representing a functional role typically found in an SME finance team.

- The **Extraction Agent** processes alternative data sources such as bank transaction files, e-commerce sales records, and OCR-extracted documents, transforming unstructured inputs into normalized financial data.
- The **Monitoring Agent** continuously evaluates financial behavior, generating a Financial Health Index and detecting anomalies or early warning signals.
- The **Forecasting Agent** predicts short-term cash flow and assesses liquidity risk under normal and stressed conditions.

These agents operate continuously, enabling proactive rather than reactive credit assessment.

---

#### 3.2.5 Intelligence & Reasoning Layer

This layer combines traditional machine learning models with large language models (LLMs). Machine learning models generate quantitative indicators such as financial strength scores and liquidity risk probabilities. LLMs provide reasoning, explanation, and recommendation generation, translating complex model outputs into human-readable insights.

A secondary LLM validation mechanism is incorporated to perform sanity checks and reduce the risk of hallucination or biased outputs, supporting governance and compliance considerations.

---

#### 3.2.6 Data Layer

The Data Layer separates structured and unstructured data storage. Structured data, including time-series financial metrics, agent outputs, and audit logs, are stored in a relational database. Unstructured data such as invoices, receipts, and OCR images are stored in object storage.

This separation enhances scalability, data governance, and compliance with financial data management practices.

---

### 3.3 System Data Flow

The system operates as a continuous loop. Alternative data is ingested and structured by the Extraction Agent, monitored by the Monitoring Agent, and projected forward by the Forecasting Agent. Agent outputs are processed by machine learning models and LLMs to generate explainable credit intelligence. Results are stored in the Data Layer and presented to users via the Presentation Layer through secure APIs.

This closed-loop design enables continuous financial transparency rather than static, document-based assessment.

---

### 3.4 Design Justification

The layered agentic architecture is chosen to address limitations of traditional SME credit scoring systems, which rely on static financial statements and limited data sources. By integrating Agentic AI, the system supports continuous monitoring, adaptive analysis, and proactive risk detection. The hybrid use of machine learning and LLMs balances predictive accuracy with explainability, a critical requirement in financial decision-making.

---

### 3.5 Chapter Summary

This chapter presented the system design and architecture of the proposed Agentic AI Credit Intelligence Platform. The layered architecture and autonomous agent framework provide a foundation for reducing information asymmetry in SME credit assessment while maintaining scalability, transparency, and regulatory alignment.

---

## 4. Research Framework

### 4.1 Research Objectives

The objectives of this Independent Study are:

1. To design and develop an **Agentic AI–based system** that transforms alternative SME data into finance-ready credit intelligence.
2. To evaluate whether **agent-driven continuous monitoring** improves SME credit readiness compared to static, document-based assessment.
3. To assess the effectiveness of **explainable AI outputs** in enhancing transparency and trust for both SMEs and lenders.
4. To demonstrate the feasibility of deploying Agentic AI within **banking and financial institution constraints**.

---

### 4.2 Research Questions (RQ)

**RQ1:** How can an Agentic AI system be designed to continuously transform alternative SME data into credit-relevant financial intelligence?

**RQ2:** To what extent does agent-based financial monitoring and forecasting improve SME credit readiness indicators?

**RQ3:** How effectively can LLM-based explanations improve the interpretability of credit assessment results for SMEs and credit analysts?

**RQ4:** What are the key design considerations required to ensure Agentic AI systems are acceptable within banking risk and governance frameworks?

---

### 4.3 Research Framework Overview

The research framework links **alternative data**, **agentic processing**, and **credit intelligence outcomes**. Alternative data sources are processed by specialized agents to generate financial health indicators, forecasts, and risk signals. These outputs are translated into explainable credit intelligence through machine learning models and LLM reasoning, which are then evaluated against defined performance metrics.

---

### 4.4 Variables and Evaluation Dimensions

#### Independent Variables
- Availability of alternative financial data
- Use of agent-based continuous monitoring
- Integration of LLM-based explanation mechanisms

#### Dependent Variables
- SME Credit Readiness Score
- Financial Health Index (FHI)
- Liquidity Risk Indicator

#### Control Variables
- SME size and industry
- Observation time window
- Data completeness level

---

### 4.5 Evaluation Metrics

| Dimension | Metric | Description |
|-------|------|-------------|
| Credit Readiness | Score improvement | Change before vs after agentic analysis |
| Predictive Utility | Forecast accuracy | Cash flow prediction error |
| Transparency | Explainability score | User understanding survey |
| Usability | SME adoption feedback | Qualitative assessment |
| Risk Insight | Early warning detection | Timeliness of alerts |

---

### 4.6 Research Methodology

This study follows a **Design Science Research (DSR)** methodology. The system artifact is iteratively designed, implemented, and evaluated using real or simulated SME data. Evaluation combines quantitative metrics (forecast accuracy, score changes) and qualitative feedback from user interactions.

---

### 4.7 Chapter Summary

This chapter established the research framework, objectives, and evaluation approach for assessing the proposed Agentic AI Credit Intelligence System. The framework ensures alignment between system design, research questions, and measurable outcomes relevant to both academic contribution and practical financial application.

---

## 5. System Implementation and Prototype Design

### 5.1 Implementation Overview

This chapter describes the implementation of the prototype system developed to demonstrate the feasibility of the proposed Agentic AI Credit Intelligence Platform. The implementation focuses on a **Minimum Viable Prototype (MVP)** that supports end-to-end data ingestion, agentic processing, credit intelligence generation, and explainable output visualization.

The prototype prioritizes functional correctness, explainability, and evaluability over full-scale production deployment.

---

### 5.2 Technology Stack

| Layer | Technology | Justification |
|-----|-----------|---------------|
| Frontend | Web-based Dashboard | Lightweight visualization for SMEs and lenders |
| Backend API | FastAPI (Python) | High performance, bank-friendly, scalable |
| Agent Framework | Custom Agent Controller | Full control over agent autonomy |
| Agent Instruction | AgentQL (DSL) | Auditability and hallucination control |
| ML Models | XGBoost / LightGBM | Strong performance on tabular financial data |
| LLM | GPT-class LLM | Reasoning, explanation, recommendation |
| Database | PostgreSQL (Supabase) | Structured financial and audit data |
| Storage | Object Storage | Documents and OCR artifacts |

---

### 5.3 Agent Design and Logic

#### 5.3.1 Extraction Agent

**Purpose:** Transform heterogeneous alternative data into normalized financial records.

**Inputs:**
- Bank transaction CSV
- E-commerce sales CSV
- OCR-extracted invoice data

**Core Logic (Pseudo-code):**
```
FOR each data_source:
    validate schema
    clean missing values
    categorize transactions
    normalize timestamps and amounts
STORE structured records
```

**Outputs:** Structured transaction table

---

#### 5.3.2 Monitoring Agent

**Purpose:** Continuously assess SME financial behavior and stability.

**Key Indicators:**
- Daily cash flow volatility
- Revenue consistency
- Expense anomaly detection
- Customer concentration ratio

**Core Logic:**
```
CALCULATE rolling metrics (30/60/90 days)
DETECT anomalies using thresholds
GENERATE Financial Health Index (FHI)
```

**Outputs:** FHI, risk flags

---

#### 5.3.3 Forecasting Agent

**Purpose:** Predict short-term liquidity risk.

**Method:**
- Time-series regression
- Seasonality-aware trend estimation

**Core Logic:**
```
TRAIN forecast model on historical cash flow
PREDICT next 30 days
SIMULATE stress scenarios
```

**Outputs:** Cash flow forecast, liquidity risk score

---

### 5.4 AgentQL Design

AgentQL is implemented as a lightweight domain-specific language to control agent execution.

**Example Query:**
```
QUERY credit_readiness
USING last_90_days_transactions
EXECUTE Extraction -> Monitoring -> Forecasting
RETURN score, risk_factors, explanation
```

This structure ensures deterministic agent behavior and traceable execution.

---

### 5.5 Machine Learning Model Design

#### Feature Engineering
- Cash inflow/outflow ratios
- Volatility metrics
- Forecasted liquidity buffer
- Behavioral stability indicators

#### Model Selection
- Gradient boosting models are selected for robustness and interpretability.

**Output:** Financial Strength Score (0–100)

---

### 5.6 LLM Reasoning and Explainability

LLMs are used to translate quantitative outputs into natural language explanations and recommendations.

**Prompt Structure:**
- Input: Scores, risk signals
- Output: Explanation, improvement suggestions

A secondary validation prompt is used to cross-check reasoning consistency.

---

### 5.7 System Constraints and Assumptions

- Prototype uses offline CSV data (no real-time open banking)
- Evaluation focuses on short-term forecasts
- Regulatory approval is out of scope for MVP

---

### 5.8 Chapter Summary

This chapter described the implementation of the prototype system, detailing the technology stack, agent design, model selection, and explainability mechanisms. The prototype demonstrates the practical feasibility of deploying Agentic AI for SME credit intelligence within real-world constraints.

