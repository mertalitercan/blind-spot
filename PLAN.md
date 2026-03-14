# TD Fraud Detection - Hackathon Project Plan

## Project name: BlindSpot

AI-powered fraud detection system that combines behavioral biometrics, cognitive state analysis, transaction graph intelligence, and LLM-based explainable reasoning to catch what traditional systems miss.

---

## 0. Railtracks integration

This project uses **Railtracks** — a Python agentic framework by Railtown AI — as the orchestration layer for our multi-agent fraud detection system. Instead of hand-rolling agent coordination, we use Railtracks' `Flow`, `agent_node`, and `function_node` primitives.

### Why Railtracks

- **Pure Python:** No YAML or DSLs. Agent behavior is defined with standard Python control flow.
- **Tool-First:** Our analysis services (behavioral, transaction, graph) become `@rt.function_node` tools that agents can invoke.
- **Async-Native:** Built-in parallelization maps perfectly to our asyncio.gather pattern for running 5 agents concurrently.
- **Built-in Observability:** Local visualizer for inspecting agent runs — great for hackathon demos.

### How Railtracks maps to our architecture

| BlindSpot concept | Railtracks primitive |
|---|---|
| Each specialist agent (behavioral, cognitive, transaction, device, graph) | `rt.agent_node()` with `rt.llm.AnthropicLLM("claude-sonnet-4-20250514")` |
| Meta-reasoning scorer | `rt.agent_node()` that receives all 5 agent outputs |
| Analysis services (behavioral_analysis, transaction_analysis, graph_service, baseline_service) | `@rt.function_node` decorated functions — automatically exposed as agent tools |
| Orchestrator pipeline | `rt.Flow()` with entry point and parallel agent execution |
| LLM calls | `rt.llm.AnthropicLLM("claude-sonnet-4-20250514")` — unified interface |

### Railtracks agent example (our pattern)

```python
import railtracks as rt

# Services become tool nodes
@rt.function_node
def compute_typing_features(keystroke_events: str) -> str:
    """Extract typing rhythm features from keystroke event data."""
    # ... feature extraction logic
    return json.dumps(features)

@rt.function_node
def compare_to_baseline(current_features: str, baseline: str) -> str:
    """Compare current behavioral features against user baseline."""
    # ... comparison logic
    return json.dumps(deviations)

# Each specialist agent is an agent_node
behavioral_agent = rt.agent_node(
    "Behavioral Biometrics Agent",
    tool_nodes=(compute_typing_features, compare_to_baseline),
    llm=rt.llm.AnthropicLLM("claude-sonnet-4-20250514"),
    system_message=BEHAVIORAL_SYSTEM_PROMPT,
)

# Orchestrator flow
fraud_detection_flow = rt.Flow(
    name="BlindSpot Detection Pipeline",
    entry_point=orchestrator_agent,
)

# Execute
result = await fraud_detection_flow.invoke(transaction_data)
```

---

## 1. Architecture overview

```
Mobile mock app (React Native / Expo)
    │
    ├── Behavioral telemetry (WebSocket) ──► FastAPI backend
    │                                            │
    └── Transaction requests (REST) ────────►    │
                                                 │
                                          ┌──────┴──────┐
                                          │ Orchestrator │
                                          │   Agent      │
                                          └──────┬──────┘
                                                 │
                     ┌───────────┬───────────┬───┴────┬──────────┐
                     │           │           │        │          │
              Behavioral   Cognitive   Transaction  Device   Graph
              Biometrics   State       Anomaly      + Session Analysis
              Agent        Agent       Agent        Agent     Agent
                     │           │           │        │          │
                     └───────────┴───────────┴───┬────┴──────────┘
                                                 │
                                          ┌──────┴──────┐
                                          │ Meta-Reasoning│
                                          │ Agent (scorer)│
                                          └──────┬──────┘
                                                 │
                                          ┌──────┴──────┐
                                          │  PostgreSQL  │
                                          │  Database    │
                                          └──────┬──────┘
                                                 │
                                          ┌──────┴──────┐
                                          │  Next.js     │
                                          │  Dashboard   │
                                          └─────────────┘
```

---

## 2. Data collection layer

### 2.1 Transaction metadata

Every transaction record includes:

- `transaction_id`: UUID
- `timestamp`: ISO 8601
- `amount`: float
- `currency`: string (CAD, USD)
- `sender_account_id`: UUID
- `recipient_account_id`: string
- `recipient_name`: string
- `recipient_institution`: string
- `transaction_type`: enum (e_transfer, bill_payment, wire, pos, atm)
- `merchant_category_code`: string (nullable)
- `ip_address`: string (IPv4/IPv6)
- `ip_geolocation`: object {lat, lng, city, country}
- `device_id`: string
- `device_fingerprint`: object (see 2.3)
- `session_id`: UUID
- `session_duration_ms`: int
- `auth_method`: enum (password, biometric, 2fa)

Derived features computed at analysis time:

- `time_since_last_transaction_seconds`: int
- `transaction_frequency_1h`: int
- `transaction_frequency_24h`: int
- `transaction_frequency_7d`: int
- `rolling_avg_amount_30d`: float
- `amount_zscore`: float (deviation from user's average)
- `is_new_recipient`: boolean
- `geo_distance_from_last_km`: float
- `is_round_number`: boolean
- `time_of_day_bucket`: enum (night_0_6, morning_6_12, afternoon_12_18, evening_18_24)
- `velocity_count_last_hour`: int
- `velocity_amount_last_hour`: float

### 2.2 Behavioral biometrics data

Collected via event listeners in the mobile mock app. Sent via WebSocket as a stream of events during the session.

**Typing dynamics:**

- `keystroke_events[]`: array of {key, timestamp_ms, dwell_time_ms, flight_time_ms}
- `typing_speed_wpm`: float (for password, amount, recipient name fields separately)
- `error_rate`: float (backspace_count / total_keystrokes)
- `typing_rhythm_signature`: float[] (inter-key timing vector, used for DTW comparison against baseline)
- `segmented_typing_detected`: boolean (pauses > 3s between character groups = dictation pattern)
- `paste_detected`: boolean (per field: password, amount, recipient_account, recipient_name)
- `paste_field`: string (which field had paste)

**Touch interaction (mobile):**

- `touch_events[]`: array of {x, y, timestamp_ms, pressure, radius, event_type}
- `avg_touch_pressure`: float
- `avg_touch_radius`: float (fingertip area)
- `swipe_velocity_avg`: float
- `scroll_speed_avg`: float
- `tap_duration_avg_ms`: float
- `gyroscope_data[]`: array of {alpha, beta, gamma, timestamp_ms} (phone orientation/angle)
- `hand_dominance`: enum (left, right, unknown) (inferred from touch coordinate distribution)

**Session behavior:**

- `navigation_path[]`: array of {screen_name, timestamp_ms, duration_ms}
- `navigation_directness_score`: float (0-1, how directly they went to the money transfer screen)
- `time_per_screen_ms`: object {screen_name: duration_ms}
- `screen_familiarity_score`: float (based on hesitation, wrong taps, back-navigation)
- `app_switches[]`: array of {timestamp_ms, duration_away_ms} (left the app and came back)
- `dead_time_periods[]`: array of {start_ms, end_ms, duration_ms} (no interaction at all)
- `total_dead_time_ms`: int
- `confirm_button_hesitation_ms`: int (time finger was near confirm but didn't press)
- `confirm_attempts`: int (how many times they approached and retreated from confirm)

### 2.3 Device fingerprint data

- `device_id`: string (persistent device identifier)
- `os`: string (iOS 17.2, Android 14)
- `os_version`: string
- `app_version`: string
- `screen_resolution`: string (1170x2532)
- `screen_density`: float
- `timezone`: string (America/Toronto)
- `language`: string (en-CA)
- `is_emulator`: boolean
- `is_rooted_jailbroken`: boolean
- `is_vpn_active`: boolean
- `is_proxy_detected`: boolean
- `is_remote_desktop_active`: boolean
- `is_screen_sharing`: boolean
- `installed_fonts_hash`: string (fingerprinting signal)
- `battery_level`: float
- `is_charging`: boolean

### 2.4 Session context data

- `is_phone_call_active`: boolean (critical for APP fraud detection)
- `phone_call_duration_ms`: int (if active)
- `clipboard_used`: boolean
- `clipboard_content_type`: enum (account_number, text, unknown)
- `notification_count_during_session`: int
- `screen_brightness`: float

### 2.5 Historical baseline data (per user, stored in DB)

- `behavioral_profile`: JSON (rolling averages of all biometric features, updated after each session)
- `transaction_profile`: JSON (typical amounts, recipients, times, frequencies)
- `device_profile`: JSON (known devices, typical IP ranges, locations)
- `known_recipients[]`: array of {recipient_id, frequency, last_used}
- `typical_session_duration_ms`: float (rolling average)
- `typical_login_times[]`: array of time ranges
- `typical_navigation_patterns`: JSON (most common screen sequences)

---

## 3. Multi-agent system

### 3.1 Agent 1: Behavioral biometrics agent

**System prompt focus:** Compare current session behavioral data against the user's historical behavioral profile.

**Input:**

```json
{
  "current_session": {
    "typing_dynamics": { ... },
    "touch_interaction": { ... },
    "session_behavior": { ... }
  },
  "user_baseline": {
    "avg_typing_speed_wpm": 42.3,
    "typing_rhythm_signature": [120, 85, 95, ...],
    "avg_touch_pressure": 0.45,
    "avg_touch_radius": 12.3,
    "hand_dominance": "right",
    "typical_navigation_directness": 0.35,
    "avg_session_duration_ms": 180000
  }
}
```

**What it analyzes:**

- Typing rhythm comparison using DTW (Dynamic Time Warping) distance
- Touch pressure distribution deviation from baseline
- Touch radius deviation (different finger or different person)
- Hand dominance consistency (right-handed user suddenly using left hand patterns)
- Navigation pattern deviation (familiarity with the app)
- Error rate comparison (more errors than usual = stress or different person)
- Session duration comparison

**Output:**

```json
{
  "behavioral_risk_score": 72,
  "confidence": 0.85,
  "flags": [
    "typing_rhythm_deviation_3.2x",
    "touch_pressure_30pct_lower",
    "navigation_directness_92pct_vs_35pct_baseline"
  ],
  "reasoning": "The typing pattern deviates significantly from the user's established rhythm. Keystroke timing shows a segmented pattern with 3-5 second pauses between groups of characters, consistent with someone being dictated information rather than typing from memory. Touch pressure is 30% lower than baseline, which could indicate a different device grip or heightened stress."
}
```

### 3.2 Agent 2: Cognitive state agent (our differentiator)

**System prompt focus:** Analyze behavioral signals through a psychological lens to determine if the user is under duress, being coached, or exhibiting stress patterns.

**Input:**

```json
{
  "session_context": {
    "is_phone_call_active": true,
    "phone_call_duration_ms": 420000,
    "dead_time_periods": [
      {"start_ms": 15000, "end_ms": 23000, "duration_ms": 8000},
      {"start_ms": 45000, "end_ms": 52000, "duration_ms": 7000}
    ],
    "total_dead_time_ms": 15000,
    "confirm_button_hesitation_ms": 4200,
    "confirm_attempts": 3,
    "paste_detected": true,
    "paste_field": "recipient_account",
    "segmented_typing_detected": true,
    "app_switches": [
      {"timestamp_ms": 30000, "duration_away_ms": 12000}
    ],
    "navigation_directness_score": 0.92,
    "time_of_day": "02:34"
  },
  "behavioral_deviations": {
    "typing_speed_ratio": 0.31,
    "error_rate_ratio": 2.8,
    "touch_pressure_ratio": 0.7
  }
}
```

**What it analyzes:**

Coercion indicators:
- Phone call active during banking session (strongest single signal)
- Segmented typing (dictation pattern)
- Dead time periods (listening to instructions)
- Paste usage on account number field (given the number, not from memory)
- App switching (checking notes/messages for instructions)
- Confirm button hesitation (internal conflict, person knows something is wrong)
- Multiple confirm attempts (approaching and retreating)

Stress indicators:
- Increased typing errors with faster speed (fight-or-flight)
- Erratic touch patterns (trembling)
- Unusual time of day for user
- Rapid scrolling without reading

Coached behavior indicators:
- Perfect navigation to unfamiliar features (being told where to click)
- Unusually slow and deliberate actions (following step-by-step)
- Character-by-character typing with pauses (being read a number)

**Output:**

```json
{
  "cognitive_risk_score": 88,
  "confidence": 0.90,
  "detected_state": "coercion_likely",
  "coercion_indicators": [
    "active_phone_call_7min",
    "segmented_typing_dictation_pattern",
    "dead_time_15s_total",
    "paste_on_recipient_account",
    "confirm_hesitation_4.2s_3_attempts"
  ],
  "stress_indicators": [
    "error_rate_2.8x_baseline",
    "unusual_time_2am"
  ],
  "coached_indicators": [
    "navigation_directness_92pct",
    "app_switch_to_notes_12s"
  ],
  "reasoning": "Strong indicators of authorized push payment fraud under phone-based social engineering. User is on a 7-minute phone call during the session. Typing shows dictation pattern (segmented input with 3-5s pauses). Account number was pasted, not typed, which is inconsistent with a genuine transfer to a known recipient. User hesitated 4.2 seconds at the confirm button and retreated 3 times before pressing, suggesting internal conflict. Dead time periods (15s total) indicate the user was listening to instructions. Transaction initiated at 2:34am, which is outside the user's normal banking hours."
}
```

### 3.3 Agent 3: Transaction anomaly agent

**Input:**

```json
{
  "current_transaction": {
    "amount": 2500.00,
    "recipient_account_id": "NEW-RECIPIENT-123",
    "recipient_name": "John Smith",
    "transaction_type": "e_transfer",
    "timestamp": "2026-03-14T02:34:00Z"
  },
  "user_transaction_history": {
    "rolling_avg_amount_30d": 312.50,
    "max_amount_90d": 800.00,
    "typical_recipients": ["rent-landlord", "mom-transfer", "netflix"],
    "typical_transaction_times": ["12:00-14:00", "18:00-20:00"],
    "transaction_count_30d": 23
  }
}
```

**What it analyzes:**

- Amount z-score (how many standard deviations from average)
- New recipient flag
- Time-of-day anomaly
- Transaction type consistency
- Round number detection
- Velocity (rapid successive transactions)
- Amount escalation pattern (small test transaction followed by large one)
- Geographic impossibility (transaction from Toronto then Lagos in 30 min)

**Output:**

```json
{
  "transaction_risk_score": 78,
  "confidence": 0.88,
  "flags": [
    "amount_8.0x_above_30d_avg",
    "new_recipient_never_contacted",
    "time_anomaly_2am_outside_normal_hours",
    "amount_exceeds_90d_max_by_3.1x"
  ],
  "reasoning": "Transaction amount of $2,500 is 8x the user's 30-day rolling average of $312.50 and 3.1x their 90-day maximum. The recipient has never been contacted before. Transaction was initiated at 2:34 AM, which is well outside the user's typical banking hours of 12-2 PM and 6-8 PM."
}
```

### 3.4 Agent 4: Device + session context agent

**Input:**

```json
{
  "device_fingerprint": { ... },
  "session_context": { ... },
  "user_device_profile": {
    "known_devices": ["iPhone-14-Pro-ABC123"],
    "typical_ip_range": "24.114.x.x",
    "typical_timezone": "America/Toronto"
  }
}
```

**What it analyzes:**

- Device recognition (known vs unknown device)
- IP address comparison against typical ranges
- VPN/proxy/Tor detection
- Emulator/simulator detection
- Rooted/jailbroken device detection
- Remote desktop / screen sharing detection
- Active phone call detection
- Clipboard usage patterns
- Timezone consistency
- Battery and charging state anomalies (emulators often show 100% plugged in)

**Output:**

```json
{
  "device_risk_score": 35,
  "confidence": 0.92,
  "flags": [
    "known_device_match",
    "ip_in_typical_range",
    "active_phone_call_detected"
  ],
  "reasoning": "Device matches the user's known iPhone 14 Pro. IP address is within their typical range. No VPN, proxy, or remote access detected. However, an active phone call was detected during the session, which is flagged as a context signal for the cognitive state agent."
}
```

### 3.5 Agent 5: Graph analysis agent

**Input:**

```json
{
  "recipient_account_id": "NEW-RECIPIENT-123",
  "recipient_graph_data": {
    "incoming_transfers_24h": 4,
    "unique_senders_24h": 4,
    "avg_sender_account_age_days": 365,
    "all_senders_first_time": true,
    "shared_ip_addresses": [],
    "shared_device_fingerprints": [],
    "recipient_account_age_days": 3
  },
  "sender_graph_data": {
    "outgoing_transfers_to_new_recipients_7d": 0,
    "connection_to_flagged_accounts": false
  }
}
```

**What it analyzes:**

- Recipient account incoming transfer patterns (multiple first-time senders = mule)
- Recipient account age (new accounts receiving large transfers = suspicious)
- Shared attributes between senders to the same recipient (same IP, device, subnet)
- Circular transaction patterns (A -> B -> C -> A)
- Fan-out patterns (one account sending to many new recipients rapidly)
- Fan-in patterns (many accounts sending to one recipient)
- Connection to previously flagged accounts

**Output:**

```json
{
  "graph_risk_score": 82,
  "confidence": 0.78,
  "flags": [
    "recipient_received_4_first_time_transfers_24h",
    "recipient_account_age_3_days",
    "fan_in_pattern_detected"
  ],
  "reasoning": "The recipient account is only 3 days old and has received transfers from 4 different first-time senders in the last 24 hours. All senders had no prior relationship with this account. This fan-in pattern to a new account is strongly consistent with a money mule account used to collect and launder fraudulently obtained funds."
}
```

### 3.6 Agent 6: Meta-reasoning agent (scorer)

**Input:** All 5 agent outputs + raw data

**Scoring model:**

```python
# Base weighted average
base_score = (
    behavioral_score * 0.20 +
    cognitive_score * 0.30 +
    transaction_score * 0.20 +
    device_score * 0.10 +
    graph_score * 0.20
)

# Amplification factors for dangerous combinations
if cognitive_score > 70 and device_score < 50:
    # Coercion on legitimate device = APP fraud pattern
    base_score *= 1.4

if cognitive_score > 70 and behavioral_score > 70:
    # Stressed AND different behavior = high confidence
    base_score *= 1.3

if graph_score > 70 and transaction_score > 60:
    # Mule recipient AND unusual transaction
    base_score *= 1.3

if behavioral_score > 80 and device_score > 80:
    # Different person on different device = ATO
    base_score *= 1.4

cumulative_score = min(round(base_score), 100)
```

The LLM meta-agent can override the formula with reasoning. It receives the formula output AND all agent reasoning, then decides if the formula output makes sense or needs adjustment.

**Output:**

```json
{
  "cumulative_fraud_score": 94,
  "risk_level": "critical",
  "recommended_action": "block_and_verify",
  "fraud_type_assessment": {
    "authorized_push_payment": 0.85,
    "account_takeover": 0.05,
    "money_mule": 0.08,
    "legitimate": 0.02
  },
  "reasoning": "Multiple agents converge on a high-confidence authorized push payment fraud pattern. The user is on their own device (device score low) but exhibiting strong coercion indicators: active phone call, dictation-pattern typing, paste on recipient account, confirm hesitation with 3 retreat attempts. The transaction is 8x above average to a brand-new recipient at 2:34 AM. The recipient account is a 3-day-old account receiving fan-in transfers from 4 first-time senders. This combination of behavioral coercion signals, anomalous transaction parameters, and suspicious recipient profile is consistent with phone-based social engineering directing the victim to transfer funds to a mule account.",
  "recommended_actions": [
    "Block transaction immediately",
    "Trigger outbound call to customer from fraud team",
    "Apply 30-minute cooling period on account",
    "Flag recipient account for investigation",
    "Log all session telemetry for forensic review"
  ],
  "agent_summary": {
    "behavioral": {"score": 72, "key_flag": "typing_rhythm_deviation_3.2x"},
    "cognitive": {"score": 88, "key_flag": "coercion_likely_phone_call_active"},
    "transaction": {"score": 78, "key_flag": "amount_8x_above_average"},
    "device": {"score": 35, "key_flag": "known_device_phone_call_active"},
    "graph": {"score": 82, "key_flag": "recipient_fan_in_mule_pattern"}
  }
}
```

---

## 4. Tech stack

| Component | Technology | Notes |
|-----------|-----------|-------|
| Mobile mock app | React Native (Expo) | TD-style UI, behavioral telemetry capture |
| Backend API | FastAPI (Python 3.11+) | REST + WebSocket endpoints |
| Agent orchestration | **Railtracks** + Anthropic SDK | Railtracks Flow/agent_node for orchestration, Claude Sonnet for all agents |
| Database | PostgreSQL 16 | With pgvector if needed for embeddings |
| Dashboard | Next.js 14 + React + Tailwind + shadcn/ui + Recharts | Real-time fraud monitoring |
| Real-time | WebSocket (FastAPI) | Behavioral telemetry streaming |
| Seed data | Python scripts with Faker | Realistic demo data generation |

---

## 5. Database schema

```sql
-- Users (mock banking customers)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    account_number VARCHAR(20) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Behavioral profiles (rolling baselines per user)
CREATE TABLE behavioral_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    avg_typing_speed_wpm FLOAT,
    typing_rhythm_signature JSONB,
    avg_touch_pressure FLOAT,
    avg_touch_radius FLOAT,
    hand_dominance VARCHAR(10),
    avg_session_duration_ms INT,
    typical_navigation_directness FLOAT,
    typical_login_hours JSONB,
    typical_error_rate FLOAT,
    sample_count INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Transaction history
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    amount DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CAD',
    recipient_account_id VARCHAR(50),
    recipient_name VARCHAR(255),
    recipient_institution VARCHAR(255),
    transaction_type VARCHAR(20) NOT NULL,
    ip_address VARCHAR(45),
    ip_geolocation JSONB,
    device_id VARCHAR(255),
    device_fingerprint JSONB,
    session_id UUID,
    auth_method VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Behavioral sessions (raw telemetry per session)
CREATE TABLE behavioral_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    session_id UUID NOT NULL,
    transaction_id UUID REFERENCES transactions(id),
    keystroke_events JSONB,
    touch_events JSONB,
    navigation_path JSONB,
    session_context JSONB,
    device_fingerprint JSONB,
    raw_telemetry JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Device profiles (known devices per user)
CREATE TABLE device_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    device_id VARCHAR(255) NOT NULL,
    device_info JSONB,
    typical_ip_ranges JSONB,
    first_seen_at TIMESTAMP DEFAULT NOW(),
    last_seen_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, device_id)
);

-- Fraud assessments (all agent outputs per transaction)
CREATE TABLE fraud_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID REFERENCES transactions(id),
    session_id UUID,
    behavioral_score INT,
    behavioral_reasoning TEXT,
    behavioral_flags JSONB,
    cognitive_score INT,
    cognitive_reasoning TEXT,
    cognitive_flags JSONB,
    cognitive_detected_state VARCHAR(50),
    transaction_score INT,
    transaction_reasoning TEXT,
    transaction_flags JSONB,
    device_score INT,
    device_reasoning TEXT,
    device_flags JSONB,
    graph_score INT,
    graph_reasoning TEXT,
    graph_flags JSONB,
    cumulative_score INT NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    fraud_type_assessment JSONB,
    recommended_action VARCHAR(50),
    recommended_actions JSONB,
    meta_reasoning TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Recipient profiles (for graph analysis)
CREATE TABLE recipient_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id VARCHAR(50) UNIQUE NOT NULL,
    account_name VARCHAR(255),
    first_seen_at TIMESTAMP DEFAULT NOW(),
    incoming_transfer_count INT DEFAULT 0,
    unique_sender_count INT DEFAULT 0,
    flagged BOOLEAN DEFAULT FALSE,
    risk_notes TEXT
);

-- Alerts (for dashboard)
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID REFERENCES transactions(id),
    assessment_id UUID REFERENCES fraud_assessments(id),
    user_id UUID REFERENCES users(id),
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'open',
    resolved_at TIMESTAMP,
    resolved_by VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);
CREATE INDEX idx_transactions_recipient ON transactions(recipient_account_id);
CREATE INDEX idx_behavioral_sessions_user ON behavioral_sessions(user_id);
CREATE INDEX idx_behavioral_sessions_session ON behavioral_sessions(session_id);
CREATE INDEX idx_fraud_assessments_transaction ON fraud_assessments(transaction_id);
CREATE INDEX idx_fraud_assessments_score ON fraud_assessments(cumulative_score);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_recipient_profiles_account ON recipient_profiles(account_id);
```

---

## 6. API endpoints

### Backend (FastAPI)

```
POST   /api/transactions              Submit a new transaction for analysis
GET    /api/transactions               List transactions (with filters)
GET    /api/transactions/{id}          Get transaction details + assessment

POST   /api/sessions/telemetry         Submit behavioral telemetry batch
WS     /ws/telemetry/{session_id}      Real-time behavioral data stream

GET    /api/assessments/{transaction_id}  Get full fraud assessment
GET    /api/assessments/recent            Recent assessments for dashboard

GET    /api/dashboard/overview         Dashboard summary stats
GET    /api/dashboard/alerts           Active alerts
GET    /api/dashboard/user/{user_id}   User profile + risk history
GET    /api/dashboard/graph/{recipient_id}  Transaction graph for recipient

PATCH  /api/alerts/{id}                Update alert status (resolve, escalate)

GET    /api/users                      List mock users
GET    /api/users/{id}                 User details + baseline

POST   /api/demo/scenario/{scenario}   Trigger a pre-built demo scenario
POST   /api/seed                       Seed the database with demo data
```

---

## 7. Project structure

```
blindspot/
├── backend/
│   ├── main.py                          # FastAPI app entry point
│   ├── config.py                        # Environment config, API keys
│   ├── database.py                      # SQLAlchemy engine + session
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py                      # Base agent class (shared LLM call logic)
│   │   ├── orchestrator.py              # Coordinates all agents, manages flow
│   │   ├── behavioral.py                # Agent 1: Behavioral biometrics
│   │   ├── cognitive.py                 # Agent 2: Cognitive state analysis
│   │   ├── transaction.py               # Agent 3: Transaction anomaly
│   │   ├── device.py                    # Agent 4: Device + session context
│   │   ├── graph.py                     # Agent 5: Graph analysis
│   │   └── meta_scorer.py              # Agent 6: Meta-reasoning scorer
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database_models.py           # SQLAlchemy ORM models
│   │   └── schemas.py                   # Pydantic request/response schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── transactions.py              # Transaction endpoints
│   │   ├── dashboard.py                 # Dashboard data endpoints
│   │   ├── assessments.py               # Fraud assessment endpoints
│   │   ├── alerts.py                    # Alert management endpoints
│   │   ├── users.py                     # User management endpoints
│   │   ├── demo.py                      # Demo scenario endpoints
│   │   └── websocket.py                 # WebSocket for telemetry
│   ├── services/
│   │   ├── __init__.py
│   │   ├── behavioral_analysis.py       # Behavioral data processing + feature extraction
│   │   ├── transaction_analysis.py      # Transaction feature computation
│   │   ├── baseline_service.py          # User baseline computation + updates
│   │   ├── graph_service.py             # Transaction graph queries
│   │   └── telemetry_service.py         # Raw telemetry ingestion
│   ├── seed/
│   │   ├── __init__.py
│   │   ├── seed_users.py                # Generate mock users
│   │   ├── seed_transactions.py         # Generate transaction history
│   │   ├── seed_behavioral.py           # Generate behavioral baselines
│   │   └── seed_scenarios.py            # Pre-built demo scenarios
│   ├── requirements.txt
│   └── alembic/                         # DB migrations (optional for hackathon)
│       └── ...
│
├── dashboard/
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx                 # Main dashboard page
│   │   │   ├── transactions/
│   │   │   │   ├── page.tsx             # Transaction list
│   │   │   │   └── [id]/page.tsx        # Transaction detail + assessment
│   │   │   ├── alerts/
│   │   │   │   └── page.tsx             # Alerts management
│   │   │   └── users/
│   │   │       └── [id]/page.tsx        # User risk profile
│   │   ├── components/
│   │   │   ├── FraudScoreGauge.tsx      # Circular gauge for cumulative score
│   │   │   ├── AgentBreakdown.tsx       # Per-agent score cards with reasoning
│   │   │   ├── TransactionTimeline.tsx  # Timeline of recent transactions
│   │   │   ├── BehavioralChart.tsx      # Typing rhythm, touch pressure charts
│   │   │   ├── CognitiveStateCard.tsx   # Cognitive state indicators visual
│   │   │   ├── DeviceInfoCard.tsx       # Device details
│   │   │   ├── GraphVisualization.tsx   # Transaction graph (d3 or recharts)
│   │   │   ├── AlertsPanel.tsx          # Active alerts list
│   │   │   ├── RiskLevelBadge.tsx       # Color-coded risk level
│   │   │   ├── ReasoningPanel.tsx       # Expandable LLM reasoning text
│   │   │   └── DemoControls.tsx         # Buttons to trigger demo scenarios
│   │   └── lib/
│   │       ├── api.ts                   # API client (fetch wrapper)
│   │       └── types.ts                 # TypeScript types matching backend schemas
│   └── public/
│       └── ...
│
├── mobile/                              # (Phase 3, for demo only)
│   └── ...
│
├── PLAN.md                              # This file
├── CLAUDE.md                            # Claude Code instructions
└── README.md
```

---

## 8. Implementation phases

### Phase 1: Backend + agents (priority, build first)

1. Set up FastAPI project structure, config, database connection
2. Create all SQLAlchemy models and Pydantic schemas
3. Write database init script (create tables)
4. Implement seed data generation (users, transaction history, behavioral baselines)
5. Implement Agent base class with shared LLM call logic
6. Implement all 6 agents with their system prompts and structured output
7. Implement orchestrator that calls agents in parallel and collects results
8. Implement transaction submission endpoint (triggers full analysis pipeline)
9. Implement all dashboard data endpoints
10. Implement demo scenario endpoint (triggers pre-built fraud scenarios)

### Phase 2: Dashboard (build second)

1. Set up Next.js project with Tailwind + shadcn/ui
2. Build main dashboard layout with sidebar navigation
3. Implement FraudScoreGauge (the big circular score display)
4. Implement AgentBreakdown (5 cards showing per-agent scores + reasoning)
5. Implement TransactionTimeline
6. Implement CognitiveStateCard (visual indicators for coercion/stress/coached)
7. Implement GraphVisualization (transaction network graph)
8. Implement AlertsPanel
9. Implement DemoControls (trigger scenarios from dashboard)
10. Connect all components to backend API

### Phase 3: Mobile mock (build last, only for demo)

1. Basic TD-style login screen
2. Account overview screen
3. Send money flow (recipient, amount, confirm)
4. Behavioral telemetry capture (typing events, touch events)
5. WebSocket connection to backend for real-time telemetry
6. Connect to transaction submission endpoint

---

## 9. Demo scenarios (pre-built)

### Scenario A: Normal transaction (baseline)

- User: Sarah Chen, regular customer
- Action: Sends $45 to her saved landlord for utilities
- Time: 6:15 PM (normal for her)
- Behavior: Normal typing speed, familiar navigation, known recipient
- Expected result: All scores low (5-15), green across the board

### Scenario B: APP fraud under coercion (the showstopper)

- User: James Wilson, regular customer
- Action: Sends $2,500 to a brand new recipient
- Time: 2:34 AM (unusual)
- Behavior: On phone call, segmented typing, paste on account field, 3 confirm hesitations, direct navigation
- Recipient: 3-day old account with 4 other first-time incoming transfers
- Expected result: Cumulative score 94, cognitive state "coercion_likely", recommended block

### Scenario C: Account takeover

- User: Maria Garcia, regular customer
- Action: Changes email, then sends $1,200 to new recipient
- Time: 3:00 PM (normal)
- Behavior: Different typing rhythm, different touch pressure, unfamiliar navigation (exploring the app)
- Device: Known device (stolen phone)
- Expected result: High behavioral score, moderate transaction score, ATO detected

### Scenario D: Money mule network

- User: Tom Brown, new account (7 days old)
- Action: Receives $500 from 3 different users, then sends $1,400 to an external account
- Behavior: Very fast, practiced navigation (done this before), no hesitation
- Expected result: Graph agent detects fan-in pattern, meta-agent identifies mule behavior

---

## 10. Key technical decisions

1. **All agents use Claude Sonnet via Railtracks** (`rt.llm.AnthropicLLM`). We need sub-5-second total analysis time for demo.
2. **Agents run in parallel** via Railtracks Flow (async-native) except the meta-agent which runs last.
3. **Structured output** via JSON mode in Claude API. Each agent returns a strict schema.
4. **Seed data is critical.** We need realistic behavioral baselines so the demo scenarios produce meaningful deviations. Generate 30+ days of transaction history per demo user.
5. **The cognitive state agent is our pitch.** Make sure its reasoning is the most detailed and impressive.
6. **Dashboard design should be dark theme** with TD green (#34A853 or similar) accents. Professional, not flashy.
7. **Graph visualization** should be simple and clear. Use recharts or d3-force for the transaction network. Don't over-engineer.
8. **No authentication needed** for the hackathon. The dashboard is open. The mobile app auto-logs in.
