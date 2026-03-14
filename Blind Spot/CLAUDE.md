# CLAUDE.md - Claude Code Instructions for FraudSense

## Project context

FraudSense is a hackathon project for TD Bank's "Best AI Hack to Detect Financial Fraud" challenge. It's a multi-agent fraud detection system that combines behavioral biometrics, cognitive state analysis, transaction graph intelligence, and LLM-based explainable reasoning.

Read PLAN.md for full architecture, data schemas, agent specifications, and implementation phases.

---

## Critical rules

- ALWAYS read PLAN.md before starting any task. It contains the complete spec.
- NEVER skip error handling. Every endpoint, every agent call, every DB query needs try/except.
- NEVER hardcode API keys. Use environment variables via python-dotenv.
- ALWAYS use async/await for FastAPI endpoints and agent calls.
- ALWAYS run agents in parallel with asyncio.gather (except meta-agent which depends on others).
- ALWAYS return structured JSON from agents. Use Pydantic models for validation.
- NEVER leave placeholder/TODO comments. Implement everything fully.
- When writing agent system prompts, make them detailed and specific. The quality of agent output depends on prompt quality.
- Test each component as you build it. Don't build everything then test at the end.

---

## Tech stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), asyncpg, Pydantic v2
- **LLM:** Anthropic Claude API (claude-sonnet-4-20250514), use `anthropic` Python SDK
- **Database:** PostgreSQL 16
- **Dashboard:** Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui, Recharts
- **Mobile (later):** React Native with Expo

---

## Project structure

```
fraudsense/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── orchestrator.py
│   │   ├── behavioral.py
│   │   ├── cognitive.py
│   │   ├── transaction.py
│   │   ├── device.py
│   │   ├── graph.py
│   │   └── meta_scorer.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database_models.py
│   │   └── schemas.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── transactions.py
│   │   ├── dashboard.py
│   │   ├── assessments.py
│   │   ├── alerts.py
│   │   ├── users.py
│   │   ├── demo.py
│   │   └── websocket.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── behavioral_analysis.py
│   │   ├── transaction_analysis.py
│   │   ├── baseline_service.py
│   │   ├── graph_service.py
│   │   └── telemetry_service.py
│   ├── seed/
│   │   ├── __init__.py
│   │   ├── seed_users.py
│   │   ├── seed_transactions.py
│   │   ├── seed_behavioral.py
│   │   └── seed_scenarios.py
│   └── requirements.txt
├── dashboard/
│   └── (Next.js project)
├── PLAN.md
├── CLAUDE.md
└── README.md
```

---

## Implementation order

Follow this exact order. Do not skip ahead.

### Phase 1: Backend foundation

**Step 1: Project setup**
```bash
mkdir -p fraudsense/backend/{agents,models,routers,services,seed}
cd fraudsense/backend
```

Create `requirements.txt`:
```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy[asyncio]==2.0.35
asyncpg==0.29.0
pydantic==2.9.0
pydantic-settings==2.5.0
python-dotenv==1.0.1
anthropic==0.39.0
httpx==0.27.0
faker==30.0.0
numpy==1.26.4
python-dateutil==2.9.0
websockets==13.0
```

Create `.env`:
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/fraudsense
ANTHROPIC_API_KEY=sk-ant-...
```

**Step 2: config.py**
- Use pydantic-settings BaseSettings
- Load from .env
- Export DATABASE_URL, ANTHROPIC_API_KEY, MODEL_NAME (default: claude-sonnet-4-20250514)

**Step 3: database.py**
- Create async SQLAlchemy engine and sessionmaker
- Create Base declarative base
- Create get_db dependency for FastAPI
- Create init_db function that creates all tables

**Step 4: models/database_models.py**
- Implement ALL tables from PLAN.md Section 5
- Use SQLAlchemy 2.0 mapped_column style
- All JSONB columns use sqlalchemy.dialects.postgresql.JSONB

**Step 5: models/schemas.py**
- Pydantic v2 models for every request/response
- TransactionCreate, TransactionResponse
- BehavioralTelemetry (the big one with all behavioral fields)
- FraudAssessmentResponse (all agent scores + reasoning)
- DashboardOverview, AlertResponse, UserResponse
- AgentOutput (shared schema for all agent responses)
- DemoScenarioRequest

### Phase 2: Agents

**Step 6: agents/base.py**
- BaseAgent class with:
  - `__init__(self, client: anthropic.AsyncAnthropic, model: str)`
  - `async def analyze(self, data: dict) -> dict`
  - `async def _call_llm(self, system_prompt: str, user_message: str) -> dict`
  - The _call_llm method should:
    - Call Claude API with JSON mode
    - Parse the response
    - Handle errors gracefully (return a default low-risk score on failure)
    - Log the raw response for debugging

**Step 7: agents/behavioral.py**
- Inherits BaseAgent
- System prompt should be very specific about what behavioral deviations to look for
- Input: current session behavioral data + user baseline
- Computes DTW-like distance between current and baseline typing rhythms (simplified: use numpy correlation or euclidean distance)
- Output: behavioral_risk_score (0-100), confidence, flags[], reasoning

**Step 8: agents/cognitive.py**
- This is the MOST IMPORTANT agent. Spend extra effort on the system prompt.
- System prompt should explain cognitive psychology concepts: coercion indicators, stress signals, coached behavior patterns
- Input: session context data + behavioral deviations
- Must reason about combinations of signals, not just individual flags
- Output: cognitive_risk_score (0-100), confidence, detected_state, coercion_indicators[], stress_indicators[], coached_indicators[], reasoning

**Step 9: agents/transaction.py**
- Input: current transaction + user transaction history stats
- Computes z-scores, velocity checks, time-of-day anomalies
- Output: transaction_risk_score (0-100), confidence, flags[], reasoning

**Step 10: agents/device.py**
- Input: device fingerprint + session context + user device profile
- Checks device recognition, VPN/proxy, emulator, remote access, active call
- Output: device_risk_score (0-100), confidence, flags[], reasoning

**Step 11: agents/graph.py**
- Input: recipient graph data + sender graph data
- Looks for fan-in, fan-out, circular patterns, new account flags
- Output: graph_risk_score (0-100), confidence, flags[], reasoning

**Step 12: agents/meta_scorer.py**
- Input: ALL 5 agent outputs + raw transaction data
- Implements the weighted scoring formula from PLAN.md Section 3.6
- The LLM receives both the formula output AND all agent reasoning
- Can override the formula if the reasoning warrants it
- Output: cumulative_score, risk_level, fraud_type_assessment, recommended_actions[], meta_reasoning, agent_summary

**Step 13: agents/orchestrator.py**
- `async def analyze_transaction(transaction_data, behavioral_data, user_id) -> FraudAssessment`
- Fetches user baseline from DB
- Fetches user transaction history from DB
- Fetches recipient graph data from DB
- Calls agents 1-5 in parallel with asyncio.gather
- Calls agent 6 (meta) with results from 1-5
- Saves full assessment to DB
- Creates alert if score > threshold (70)
- Returns complete assessment

### Phase 3: Services

**Step 14: services/behavioral_analysis.py**
- `compute_typing_features(keystroke_events) -> dict`
- `compute_touch_features(touch_events) -> dict`
- `compute_session_features(navigation_path, session_context) -> dict`
- `compare_to_baseline(current_features, baseline) -> dict` (computes ratios/deviations)

**Step 15: services/transaction_analysis.py**
- `compute_transaction_features(transaction, history) -> dict`
- Computes z-score, velocity, time anomaly, new recipient flag, round number, etc.

**Step 16: services/graph_service.py**
- `get_recipient_graph_data(recipient_account_id, db) -> dict`
- Queries recent incoming transfers, unique senders, account age
- `get_sender_graph_data(user_id, db) -> dict`

**Step 17: services/baseline_service.py**
- `get_user_baseline(user_id, db) -> dict`
- `update_user_baseline(user_id, session_data, db)` (rolling average update)
- `get_user_transaction_history(user_id, db) -> dict` (stats for last 30/90 days)

### Phase 4: Routers

**Step 18: routers/transactions.py**
- POST /api/transactions: accepts TransactionCreate + BehavioralTelemetry, triggers orchestrator, returns assessment
- GET /api/transactions: list with pagination and filters
- GET /api/transactions/{id}: detail with assessment

**Step 19: routers/dashboard.py**
- GET /api/dashboard/overview: total transactions today, flagged count, avg score, high-risk count
- GET /api/dashboard/user/{user_id}: user profile + behavioral baseline + risk history

**Step 20: routers/assessments.py**
- GET /api/assessments/{transaction_id}: full assessment detail
- GET /api/assessments/recent: last 20 assessments ordered by score desc

**Step 21: routers/alerts.py**
- GET /api/dashboard/alerts: active alerts
- PATCH /api/alerts/{id}: update status

**Step 22: routers/demo.py**
- POST /api/demo/scenario/{scenario}: triggers a pre-built scenario (normal, app_fraud, ato, mule_network)
- Each scenario injects realistic data and triggers the full pipeline
- Returns the assessment result

**Step 23: routers/users.py**
- GET /api/users: list all demo users
- GET /api/users/{id}: user detail

**Step 24: main.py**
- Create FastAPI app
- Include all routers with /api prefix
- Add CORS middleware (allow all origins for hackathon)
- On startup: init_db, optionally seed data
- Health check endpoint at /api/health

### Phase 5: Seed data

**Step 25: seed/**
- seed_users.py: Create 4 demo users (Sarah Chen, James Wilson, Maria Garcia, Tom Brown)
- seed_transactions.py: Generate 30+ days of transaction history per user with realistic patterns
- seed_behavioral.py: Generate behavioral baselines from fake session data
- seed_scenarios.py: Define the 4 demo scenarios with all their data

### Phase 6: Dashboard

**Step 26: Dashboard setup**
```bash
cd fraudsense
npx create-next-app@latest dashboard --typescript --tailwind --eslint --app --src-dir
cd dashboard
npx shadcn@latest init
npx shadcn@latest add card badge button separator tabs scroll-area
npm install recharts
```

**Step 27: Dashboard pages and components**
- Build in this order:
  1. Layout with sidebar (logo, nav links)
  2. Main dashboard page with overview stats
  3. FraudScoreGauge (big circular gauge, color-coded)
  4. AgentBreakdown (5 cards, expandable reasoning)
  5. TransactionTimeline (list with risk badges)
  6. CognitiveStateCard (the differentiator visual)
  7. AlertsPanel
  8. DemoControls (buttons for each scenario)
  9. Transaction detail page
  10. User profile page

---

## Agent system prompt guidelines

Each agent system prompt must include:

1. **Role definition:** "You are a [specific role] agent in a fraud detection system."
2. **Task description:** Exactly what you analyze and what you're looking for.
3. **Input format:** JSON schema of what you'll receive.
4. **Output format:** Exact JSON schema you must return. No markdown, no explanation outside JSON.
5. **Scoring rubric:** What constitutes low (0-30), medium (31-60), high (61-80), critical (81-100) scores.
6. **Flag naming convention:** Use snake_case descriptive names like `typing_rhythm_deviation_3.2x`.
7. **Reasoning guidelines:** Write 2-4 sentences. Be specific with numbers. Reference the actual data values. Don't be vague.

Example system prompt structure:
```
You are the Cognitive State Analysis Agent in a real-time fraud detection system.
Your job is to analyze behavioral signals through a psychological lens to determine
if a banking user is under duress, being coached, or experiencing stress during
a transaction session.

You will receive session context data and behavioral deviation metrics.
You must analyze these signals for patterns of coercion, stress, and coached behavior.

COERCION INDICATORS (strongest signals):
- Active phone call during banking session
- Segmented typing (dictation pattern: type, pause 3+ seconds, type)
- Dead time periods (no interaction = listening to instructions)
- Paste on recipient account field (given the number, not from memory)
...

SCORING RUBRIC:
0-20: Normal session, no concerning signals
21-40: Minor anomalies, likely benign
41-60: Multiple mild signals, worth monitoring
61-80: Strong indicators of potential coercion or stress
81-100: High confidence coercion/coaching pattern detected

You MUST respond with ONLY valid JSON matching this schema:
{
  "cognitive_risk_score": <int 0-100>,
  "confidence": <float 0-1>,
  "detected_state": <"normal" | "mild_stress" | "significant_stress" | "coaching_suspected" | "coercion_likely">,
  "coercion_indicators": [<string>],
  "stress_indicators": [<string>],
  "coached_indicators": [<string>],
  "reasoning": "<string, 2-4 sentences, be specific with numbers>"
}
```

---

## Code style

- Python: use type hints everywhere, async functions, f-strings
- Use descriptive variable names, no single letter variables (except i, j in loops)
- Docstrings on all public functions
- Group imports: stdlib, third-party, local
- FastAPI routers use dependency injection for DB sessions
- Pydantic models use model_config with from_attributes=True where needed
- All datetimes in UTC

---

## Dashboard style

- Dark theme with near-black background (#0a0a0a or similar)
- TD green accent (#34A853) for positive/safe indicators
- Red (#E24B4A) for high risk, amber (#EF9F27) for medium, green for low
- Use shadcn/ui Card components for all data sections
- Recharts for all charts (line charts for trends, bar for comparisons)
- The FraudScoreGauge should be a large, prominent SVG circular gauge
- Agent reasoning should be in expandable accordion-style cards
- Use monospace font for JSON data displays
- Responsive but optimized for desktop (1440px+)

---

## Common pitfalls to avoid

1. **Don't forget CORS.** The dashboard runs on :3000, backend on :8000. Add CORSMiddleware.
2. **Don't make agents synchronous.** All LLM calls must be async.
3. **Don't forget to handle agent failures.** If one agent fails, the others should still work. Return a default score of 0 for failed agents.
4. **Don't skip seed data.** The demo is useless without realistic baselines. Agents need historical data to compare against.
5. **Don't over-engineer the graph analysis.** Simple SQL queries for fan-in/fan-out patterns are enough. Don't bring in networkx or graph databases.
6. **Don't use SQLite.** Use PostgreSQL. JSONB columns are critical.
7. **Don't forget to create __init__.py files** in every Python package directory.
8. **Don't hardcode demo scenario data in routes.** Put them in seed/seed_scenarios.py and load from DB.

---

## Environment setup

```bash
# PostgreSQL
createdb fraudsense

# Backend
cd fraudsense/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in ANTHROPIC_API_KEY

# Run backend
uvicorn main:app --reload --port 8000

# Dashboard
cd fraudsense/dashboard
npm install
npm run dev  # runs on :3000
```

---

## Testing the pipeline

After building, test with:

```bash
# 1. Seed the database
curl -X POST http://localhost:8000/api/seed

# 2. Run a normal transaction scenario
curl -X POST http://localhost:8000/api/demo/scenario/normal

# 3. Run the APP fraud scenario (the showstopper)
curl -X POST http://localhost:8000/api/demo/scenario/app_fraud

# 4. Check the dashboard at http://localhost:3000
```

The APP fraud scenario should produce a cumulative score of 85+ with detailed reasoning from all agents, especially the cognitive state agent.
