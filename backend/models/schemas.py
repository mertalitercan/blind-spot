from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class TransactionType(str, Enum):
    e_transfer = "e_transfer"
    bill_payment = "bill_payment"
    wire = "wire"
    pos = "pos"
    atm = "atm"


class AuthMethod(str, Enum):
    password = "password"
    biometric = "biometric"
    two_fa = "2fa"


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class DetectedState(str, Enum):
    normal = "normal"
    mild_stress = "mild_stress"
    significant_stress = "significant_stress"
    coaching_suspected = "coaching_suspected"
    coercion_likely = "coercion_likely"


# --- Agent Output Schemas ---

class AgentOutput(BaseModel):
    risk_score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    flags: list[str] = []
    reasoning: str = ""


class BehavioralAgentOutput(AgentOutput):
    pass


class CognitiveAgentOutput(BaseModel):
    cognitive_risk_score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    detected_state: str = "normal"
    coercion_indicators: list[str] = []
    stress_indicators: list[str] = []
    coached_indicators: list[str] = []
    reasoning: str = ""


class TransactionAgentOutput(AgentOutput):
    pass


class DeviceAgentOutput(AgentOutput):
    pass


class GraphAgentOutput(AgentOutput):
    recipient_graph_data: dict = {}


class FraudTypeAssessment(BaseModel):
    authorized_push_payment: float = 0.0
    account_takeover: float = 0.0
    money_mule: float = 0.0
    legitimate: float = 0.0


class MetaScorerOutput(BaseModel):
    cumulative_fraud_score: int = Field(ge=0, le=100)
    risk_level: str = "low"
    recommended_action: str = ""
    fraud_type_assessment: FraudTypeAssessment = FraudTypeAssessment()
    reasoning: str = ""
    recommended_actions: list[str] = []
    agent_summary: dict = {}


# --- Request/Response Schemas ---

class GeoLocation(BaseModel):
    lat: float = 0.0
    lng: float = 0.0
    city: str = ""
    country: str = ""


class DeviceFingerprint(BaseModel):
    device_id: str = ""
    os: str = ""
    os_version: str = ""
    app_version: str = ""
    screen_resolution: str = ""
    timezone: str = "America/Toronto"
    language: str = "en-CA"
    is_emulator: bool = False
    is_rooted_jailbroken: bool = False
    is_vpn_active: bool = False
    is_proxy_detected: bool = False
    is_remote_desktop_active: bool = False
    is_screen_sharing: bool = False
    battery_level: float = 0.85
    is_charging: bool = False


class SessionContext(BaseModel):
    is_phone_call_active: bool = False
    phone_call_duration_ms: int = 0
    clipboard_used: bool = False
    clipboard_content_type: str = "unknown"
    notification_count_during_session: int = 0
    screen_brightness: float = 0.7


class KeystrokeEvent(BaseModel):
    key: str = ""
    timestamp_ms: int = 0
    dwell_time_ms: int = 0
    flight_time_ms: int = 0


class TouchEvent(BaseModel):
    x: float = 0.0
    y: float = 0.0
    timestamp_ms: int = 0
    pressure: float = 0.0
    radius: float = 0.0
    event_type: str = "tap"


class NavigationStep(BaseModel):
    screen_name: str = ""
    timestamp_ms: int = 0
    duration_ms: int = 0


class AppSwitch(BaseModel):
    timestamp_ms: int = 0
    duration_away_ms: int = 0


class DeadTimePeriod(BaseModel):
    start_ms: int = 0
    end_ms: int = 0
    duration_ms: int = 0


class BehavioralTelemetry(BaseModel):
    keystroke_events: list[KeystrokeEvent] = []
    typing_speed_wpm: float = 0.0
    error_rate: float = 0.0
    typing_rhythm_signature: list[float] = []
    segmented_typing_detected: bool = False
    paste_detected: bool = False
    paste_field: str = ""
    touch_events: list[TouchEvent] = []
    avg_touch_pressure: float = 0.0
    avg_touch_radius: float = 0.0
    swipe_velocity_avg: float = 0.0
    tap_duration_avg_ms: float = 0.0
    hand_dominance: str = "right"
    navigation_path: list[NavigationStep] = []
    navigation_directness_score: float = 0.5
    time_per_screen_ms: dict = {}
    screen_familiarity_score: float = 0.5
    app_switches: list[AppSwitch] = []
    dead_time_periods: list[DeadTimePeriod] = []
    total_dead_time_ms: int = 0
    confirm_button_hesitation_ms: int = 0
    confirm_attempts: int = 1


class TransactionCreate(BaseModel):
    user_id: str
    amount: float
    currency: str = "CAD"
    recipient_account_id: str
    recipient_name: str
    recipient_institution: str = ""
    transaction_type: TransactionType = TransactionType.e_transfer
    ip_address: str = "192.168.1.1"
    ip_geolocation: GeoLocation = GeoLocation()
    device_fingerprint: DeviceFingerprint = DeviceFingerprint()
    session_context: SessionContext = SessionContext()
    auth_method: AuthMethod = AuthMethod.biometric
    behavioral_telemetry: BehavioralTelemetry = BehavioralTelemetry()
    timestamp: str = ""


class FraudAssessmentResponse(BaseModel):
    transaction_id: str = ""
    user_id: str = ""
    behavioral: BehavioralAgentOutput = BehavioralAgentOutput(risk_score=0, confidence=0.0)
    cognitive: CognitiveAgentOutput = CognitiveAgentOutput(cognitive_risk_score=0, confidence=0.0)
    transaction: TransactionAgentOutput = TransactionAgentOutput(risk_score=0, confidence=0.0)
    device: DeviceAgentOutput = DeviceAgentOutput(risk_score=0, confidence=0.0)
    graph: GraphAgentOutput = GraphAgentOutput(risk_score=0, confidence=0.0)
    meta: MetaScorerOutput = MetaScorerOutput(cumulative_fraud_score=0)
    processing_time_ms: float = 0.0


class DemoScenarioRequest(BaseModel):
    scenario: str = "normal"
