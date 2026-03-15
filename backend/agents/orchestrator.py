"""Orchestrator — coordinates all 6 agents using Railtracks to produce a full fraud assessment."""

import asyncio
import json
import time
import logging

import railtracks as rt

from agents.base import parse_agent_json
from agents.behavioral import behavioral_agent
from agents.cognitive import cognitive_agent
from agents.transaction import transaction_agent
from agents.device import device_agent
from agents.graph import graph_agent
from agents.meta_scorer import meta_scorer_agent
from seed.seed_scenarios import (
    get_user_baseline, get_recipient_graph,
    get_sender_profile, get_recipient_business_profile,
    compute_geo_distance_km,
)
from database import get_user_sessions, get_user_ip_history, save_session
from models.schemas import (
    FraudAssessmentResponse,
    BehavioralAgentOutput,
    CognitiveAgentOutput,
    TransactionAgentOutput,
    DeviceAgentOutput,
    GraphAgentOutput,
    MetaScorerOutput,
    FraudTypeAssessment,
)

logger = logging.getLogger(__name__)


def _compute_session_stats(sessions: list[dict]) -> dict:
    """Compute aggregate statistics from ALL historical sessions."""
    if not sessions:
        return {}

    def _stats(values: list[float]) -> dict:
        if not values:
            return {"mean": 0, "min": 0, "max": 0, "std": 0}
        n = len(values)
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / max(n - 1, 1)
        return {
            "mean": round(mean, 3),
            "min": round(min(values), 3),
            "max": round(max(values), 3),
            "std": round(variance ** 0.5, 3),
        }

    speeds = [s.get("typing_speed_wpm", 0) for s in sessions if s.get("typing_speed_wpm")]
    errors = [s.get("error_rate", 0) for s in sessions if s.get("error_rate") is not None]
    pressures = [s.get("avg_touch_pressure", 0) for s in sessions if s.get("avg_touch_pressure")]
    radii = [s.get("avg_touch_radius", 0) for s in sessions if s.get("avg_touch_radius")]
    directness = [s.get("navigation_directness_score", 0) for s in sessions if s.get("navigation_directness_score")]
    durations = [s.get("session_duration_ms", 0) for s in sessions if s.get("session_duration_ms")]
    hesitations = [s.get("confirm_button_hesitation_ms", 0) for s in sessions if s.get("confirm_button_hesitation_ms")]

    paste_count = sum(1 for s in sessions if s.get("paste_detected"))
    segmented_count = sum(1 for s in sessions if s.get("segmented_typing_detected"))
    devices = {}
    for s in sessions:
        d = s.get("device_id", "")
        devices[d] = devices.get(d, 0) + 1

    return {
        "total_sessions": len(sessions),
        "typing_speed_wpm": _stats(speeds),
        "error_rate": _stats(errors),
        "avg_touch_pressure": _stats(pressures),
        "avg_touch_radius": _stats(radii),
        "navigation_directness": _stats(directness),
        "session_duration_ms": _stats(durations),
        "confirm_hesitation_ms": _stats(hesitations),
        "paste_frequency": round(paste_count / len(sessions), 3),
        "segmented_typing_frequency": round(segmented_count / len(sessions), 3),
        "known_devices": devices,
    }


def _build_behavioral_input(transaction_data: dict, baseline: dict, historical_sessions: list[dict]) -> str:
    """Build the input message for the behavioral agent with full historical stats."""
    telemetry = transaction_data.get("behavioral_telemetry", {})

    # Compute aggregate stats from ALL sessions
    aggregate_stats = _compute_session_stats(historical_sessions)

    # Also include last 5 individual sessions for recency context
    recent = []
    for s in historical_sessions[:5]:
        recent.append({
            "timestamp": s.get("timestamp", ""),
            "typing_speed_wpm": s.get("typing_speed_wpm", 0),
            "error_rate": s.get("error_rate", 0),
            "avg_touch_pressure": s.get("avg_touch_pressure", 0),
            "avg_touch_radius": s.get("avg_touch_radius", 0),
            "hand_dominance": s.get("hand_dominance", "unknown"),
            "navigation_directness_score": s.get("navigation_directness_score", 0),
            "session_duration_ms": s.get("session_duration_ms", 0),
            "paste_detected": bool(s.get("paste_detected", 0)),
            "confirm_attempts": s.get("confirm_attempts", 1),
            "device_id": s.get("device_id", ""),
            "fraud_score": s.get("fraud_score", 0),
        })

    return json.dumps({
        "current_session": {
            "typing_speed_wpm": telemetry.get("typing_speed_wpm", 0),
            "error_rate": telemetry.get("error_rate", 0),
            "typing_rhythm_signature": telemetry.get("typing_rhythm_signature", []),
            "segmented_typing_detected": telemetry.get("segmented_typing_detected", False),
            "paste_detected": telemetry.get("paste_detected", False),
            "paste_field": telemetry.get("paste_field", ""),
            "avg_touch_pressure": telemetry.get("avg_touch_pressure", 0),
            "avg_touch_radius": telemetry.get("avg_touch_radius", 0),
            "hand_dominance": telemetry.get("hand_dominance", "unknown"),
            "navigation_directness_score": telemetry.get("navigation_directness_score", 0),
            "screen_familiarity_score": telemetry.get("screen_familiarity_score", 0),
            "session_duration_ms": sum(
                s.get("duration_ms", 0) for s in telemetry.get("navigation_path", [])
            ),
            "confirm_button_hesitation_ms": telemetry.get("confirm_button_hesitation_ms", 0),
            "confirm_attempts": telemetry.get("confirm_attempts", 1),
            "keystroke_events": telemetry.get("keystroke_events", []),
        },
        "user_baseline": {
            "avg_typing_speed_wpm": baseline.get("avg_typing_speed_wpm", 40),
            "typing_rhythm_signature": baseline.get("typing_rhythm_signature", []),
            "avg_touch_pressure": baseline.get("avg_touch_pressure", 0.5),
            "avg_touch_radius": baseline.get("avg_touch_radius", 12),
            "hand_dominance": baseline.get("hand_dominance", "right"),
            "typical_navigation_directness": baseline.get("typical_navigation_directness", 0.35),
            "avg_session_duration_ms": baseline.get("avg_session_duration_ms", 180000),
            "typical_error_rate": baseline.get("typical_error_rate", 0.05),
        },
        "historical_aggregate_stats": aggregate_stats,
        "recent_sessions": recent,
        "total_historical_sessions": len(historical_sessions),
    }, indent=2)


def _build_cognitive_input(transaction_data: dict, baseline: dict) -> str:
    """Build the input message for the cognitive agent."""
    telemetry = transaction_data.get("behavioral_telemetry", {})
    session_ctx = transaction_data.get("session_context", {})
    timestamp = transaction_data.get("timestamp", "")
    time_of_day = ""
    if "T" in timestamp:
        time_of_day = timestamp.split("T")[1][:5]

    typing_speed_ratio = 1.0
    baseline_speed = baseline.get("avg_typing_speed_wpm", 40)
    if baseline_speed > 0:
        typing_speed_ratio = round(telemetry.get("typing_speed_wpm", 0) / baseline_speed, 2)

    error_rate_ratio = 1.0
    baseline_error = baseline.get("typical_error_rate", 0.05)
    if baseline_error > 0:
        error_rate_ratio = round(telemetry.get("error_rate", 0) / baseline_error, 2)

    touch_pressure_ratio = 1.0
    baseline_pressure = baseline.get("avg_touch_pressure", 0.5)
    if baseline_pressure > 0:
        touch_pressure_ratio = round(telemetry.get("avg_touch_pressure", 0) / baseline_pressure, 2)

    return json.dumps({
        "session_context": {
            "is_phone_call_active": session_ctx.get("is_phone_call_active", False),
            "phone_call_duration_ms": session_ctx.get("phone_call_duration_ms", 0),
            "dead_time_periods": telemetry.get("dead_time_periods", []),
            "total_dead_time_ms": telemetry.get("total_dead_time_ms", 0),
            "confirm_button_hesitation_ms": telemetry.get("confirm_button_hesitation_ms", 0),
            "confirm_attempts": telemetry.get("confirm_attempts", 1),
            "paste_detected": telemetry.get("paste_detected", False),
            "paste_field": telemetry.get("paste_field", ""),
            "segmented_typing_detected": telemetry.get("segmented_typing_detected", False),
            "app_switches": telemetry.get("app_switches", []),
            "navigation_directness_score": telemetry.get("navigation_directness_score", 0),
            "time_of_day": time_of_day,
            "clipboard_used": session_ctx.get("clipboard_used", False),
            "clipboard_content_type": session_ctx.get("clipboard_content_type", "unknown"),
        },
        "behavioral_deviations": {
            "typing_speed_ratio": typing_speed_ratio,
            "error_rate_ratio": error_rate_ratio,
            "touch_pressure_ratio": touch_pressure_ratio,
        },
    }, indent=2)


def _build_transaction_input(transaction_data: dict, baseline: dict, sender_profile: dict, recipient_profile: dict, geo_distance_km: float) -> str:
    """Build the input message for the transaction agent with full context."""
    history = baseline.get("transaction_history", {})
    geo = transaction_data.get("ip_geolocation", {})
    sender_loc = sender_profile.get("typical_location", {})

    return json.dumps({
        "current_transaction": {
            "amount": transaction_data.get("amount", 0),
            "currency": transaction_data.get("currency", "CAD"),
            "recipient_account_id": transaction_data.get("recipient_account_id", ""),
            "recipient_name": transaction_data.get("recipient_name", ""),
            "recipient_institution": transaction_data.get("recipient_institution", ""),
            "transaction_type": transaction_data.get("transaction_type", "e_transfer"),
            "timestamp": transaction_data.get("timestamp", ""),
            "ip_address": transaction_data.get("ip_address", ""),
            "ip_geolocation": geo,
        },
        "user_transaction_history": {
            "rolling_avg_amount_30d": history.get("rolling_avg_amount_30d", 0),
            "max_amount_90d": history.get("max_amount_90d", 0),
            "std_dev_amount_30d": history.get("std_dev_amount_30d", 0),
            "typical_recipients": history.get("typical_recipients", []),
            "typical_transaction_times": history.get("typical_transaction_times", []),
            "transaction_count_30d": history.get("transaction_count_30d", 0),
        },
        "sender_profile": {
            "account_type": sender_profile.get("account_type", "personal"),
            "occupation": sender_profile.get("occupation", "Unknown"),
            "employer": sender_profile.get("employer", "Unknown"),
            "industry": sender_profile.get("industry", "unknown"),
            "account_age_days": sender_profile.get("account_age_days", 365),
            "monthly_income_range": sender_profile.get("monthly_income_range", "0-0"),
            "typical_location": sender_loc,
        },
        "recipient_business_profile": {
            "business_name": recipient_profile.get("business_name", "Unknown"),
            "business_type": recipient_profile.get("business_type", "unknown"),
            "industry": recipient_profile.get("industry", "unknown"),
            "mcc_code": recipient_profile.get("mcc_code"),
            "mcc_description": recipient_profile.get("mcc_description", "Unknown"),
            "registered_address": recipient_profile.get("registered_address"),
            "years_in_business": recipient_profile.get("years_in_business", 0),
            "website": recipient_profile.get("website"),
        },
        "geolocation_analysis": {
            "current_ip_city": geo.get("city", "Unknown"),
            "current_ip_country": geo.get("country", "Unknown"),
            "typical_city": sender_loc.get("city", "Toronto"),
            "typical_country": sender_loc.get("country", "CA"),
            "distance_from_typical_km": round(geo_distance_km, 1),
            "location_match": geo_distance_km < 50,
        },
    }, indent=2)


def _build_device_input(transaction_data: dict, baseline: dict, ip_history: list[dict], geo_distance_km: float) -> str:
    """Build the input message for the device agent with IP history and geolocation."""
    geo = transaction_data.get("ip_geolocation", {})
    sender_profile = get_sender_profile(transaction_data.get("user_id", ""))
    sender_loc = sender_profile.get("typical_location", {})

    # Summarize IP history
    ip_summary = []
    for ip_rec in ip_history[:10]:
        ip_summary.append({
            "ip_address": ip_rec.get("ip_address", ""),
            "city": ip_rec.get("ip_city", ""),
            "country": ip_rec.get("ip_country", ""),
            "login_count": ip_rec.get("login_count", 0),
            "last_seen": ip_rec.get("last_seen", ""),
        })

    current_ip = transaction_data.get("ip_address", "")
    ip_seen_before = any(rec.get("ip_address") == current_ip for rec in ip_history)

    return json.dumps({
        "device_fingerprint": transaction_data.get("device_fingerprint", {}),
        "session_context": transaction_data.get("session_context", {}),
        "user_device_profile": {
            "known_devices": baseline.get("known_devices", []),
            "typical_ip_range": baseline.get("typical_ip_range", ""),
            "typical_timezone": baseline.get("typical_timezone", "America/Toronto"),
        },
        "geolocation_analysis": {
            "current_ip": current_ip,
            "current_ip_city": geo.get("city", "Unknown"),
            "current_ip_country": geo.get("country", "Unknown"),
            "current_ip_lat": geo.get("lat", 0),
            "current_ip_lng": geo.get("lng", 0),
            "typical_city": sender_loc.get("city", "Toronto"),
            "typical_country": sender_loc.get("country", "CA"),
            "distance_from_typical_km": round(geo_distance_km, 1),
            "ip_seen_before": ip_seen_before,
        },
        "ip_login_history": ip_summary,
    }, indent=2)


def _build_graph_input(transaction_data: dict, recipient_graph: dict) -> str:
    """Build the input message for the graph agent."""
    return json.dumps({
        "recipient_account_id": transaction_data.get("recipient_account_id", ""),
        "recipient_graph_data": recipient_graph,
        "sender_graph_data": {
            "outgoing_transfers_to_new_recipients_7d": 0,
            "connection_to_flagged_accounts": False,
        },
    }, indent=2)


def _compute_formula_score(scores: dict) -> int:
    """Compute the weighted formula score with amplification."""
    base_score = (
        scores.get("behavioral", 0) * 0.20
        + scores.get("cognitive", 0) * 0.30
        + scores.get("transaction", 0) * 0.20
        + scores.get("device", 0) * 0.10
        + scores.get("graph", 0) * 0.20
    )

    cognitive = scores.get("cognitive", 0)
    behavioral = scores.get("behavioral", 0)
    device = scores.get("device", 0)
    graph = scores.get("graph", 0)
    transaction = scores.get("transaction", 0)

    if cognitive > 70 and device < 50:
        base_score *= 1.4
    if cognitive > 70 and behavioral > 70:
        base_score *= 1.3
    if graph > 70 and transaction > 60:
        base_score *= 1.3
    if behavioral > 80 and device > 80:
        base_score *= 1.4

    return min(round(base_score), 100)


def _build_meta_input(
    scores: dict,
    behavioral_result: dict,
    cognitive_result: dict,
    transaction_result: dict,
    device_result: dict,
    graph_result: dict,
    formula_score: int,
    transaction_data: dict,
) -> str:
    """Build the input message for the meta-reasoning agent."""
    return json.dumps({
        "formula_score": formula_score,
        "individual_scores": scores,
        "agent_outputs": {
            "behavioral": behavioral_result,
            "cognitive": cognitive_result,
            "transaction": transaction_result,
            "device": device_result,
            "graph": graph_result,
        },
        "transaction_summary": {
            "amount": transaction_data.get("amount", 0),
            "currency": transaction_data.get("currency", "CAD"),
            "recipient": transaction_data.get("recipient_name", ""),
            "recipient_account_id": transaction_data.get("recipient_account_id", ""),
            "recipient_institution": transaction_data.get("recipient_institution", ""),
            "timestamp": transaction_data.get("timestamp", ""),
            "transaction_type": transaction_data.get("transaction_type", ""),
            "ip_address": transaction_data.get("ip_address", ""),
            "ip_geolocation": transaction_data.get("ip_geolocation", {}),
        },
    }, indent=2)


async def _call_agent_safe(agent, input_msg: str, agent_name: str, retries: int = 2) -> dict:
    """Call an agent with error handling and rate limit retry."""
    for attempt in range(retries + 1):
        try:
            result = await rt.call(agent, input_msg)
            text = result.text if hasattr(result, "text") else str(result)
            parsed = parse_agent_json(text)
            if parsed and any(k in parsed for k in ("risk_score", "cognitive_risk_score", "cumulative_fraud_score")):
                return parsed
            logger.warning(f"{agent_name} returned unparseable response: {text[:300]}")
            return {"risk_score": 0, "confidence": 0.0, "flags": [], "reasoning": f"{agent_name} failed to produce valid output."}
        except Exception as e:
            error_str = str(e)
            if "rate_limit" in error_str.lower() and attempt < retries:
                logger.warning(f"{agent_name} hit rate limit, retrying in {3 * (attempt + 1)}s...")
                await asyncio.sleep(3 * (attempt + 1))
                continue
            logger.error(f"{agent_name} failed: {e}")
            return {"risk_score": 0, "confidence": 0.0, "flags": [], "reasoning": f"{agent_name} encountered an error: {str(e)}"}


async def analyze_transaction(transaction_data: dict) -> FraudAssessmentResponse:
    """Run the full fraud detection pipeline on a transaction.

    Args:
        transaction_data: Full transaction data including behavioral telemetry.

    Returns:
        FraudAssessmentResponse with all agent scores and meta assessment.
    """
    start_time = time.time()

    user_id = transaction_data.get("user_id", "")
    baseline = get_user_baseline(user_id)
    recipient_graph = get_recipient_graph(transaction_data.get("recipient_account_id", ""))
    sender_profile = get_sender_profile(user_id)
    recipient_profile = get_recipient_business_profile(transaction_data.get("recipient_account_id", ""))

    # Get historical data from database
    historical_sessions = get_user_sessions(user_id, limit=1000)
    ip_history = get_user_ip_history(user_id)

    # Compute geolocation distance
    geo = transaction_data.get("ip_geolocation", {})
    sender_loc = sender_profile.get("typical_location", {})
    geo_distance_km = compute_geo_distance_km(
        sender_loc.get("lat", 43.65), sender_loc.get("lng", -79.38),
        geo.get("lat", 43.65), geo.get("lng", -79.38),
    )

    # Build inputs for each agent
    behavioral_input = _build_behavioral_input(transaction_data, baseline, historical_sessions)
    cognitive_input = _build_cognitive_input(transaction_data, baseline)
    transaction_input = _build_transaction_input(transaction_data, baseline, sender_profile, recipient_profile, geo_distance_km)
    device_input = _build_device_input(transaction_data, baseline, ip_history, geo_distance_km)
    graph_input = _build_graph_input(transaction_data, recipient_graph)

    # Run agents in two staggered batches to avoid rate limits
    behavioral_result, cognitive_result, transaction_result = await asyncio.gather(
        _call_agent_safe(behavioral_agent, behavioral_input, "Behavioral"),
        _call_agent_safe(cognitive_agent, cognitive_input, "Cognitive"),
        _call_agent_safe(transaction_agent, transaction_input, "Transaction"),
    )
    await asyncio.sleep(2)  # brief pause to respect rate limits
    device_result, graph_result = await asyncio.gather(
        _call_agent_safe(device_agent, device_input, "Device"),
        _call_agent_safe(graph_agent, graph_input, "Graph"),
    )

    # Extract scores
    scores = {
        "behavioral": behavioral_result.get("risk_score", 0),
        "cognitive": cognitive_result.get("cognitive_risk_score", cognitive_result.get("risk_score", 0)),
        "transaction": transaction_result.get("risk_score", 0),
        "device": device_result.get("risk_score", 0),
        "graph": graph_result.get("risk_score", 0),
    }

    formula_score = _compute_formula_score(scores)

    # Run meta-reasoning agent
    meta_input = _build_meta_input(
        scores, behavioral_result, cognitive_result,
        transaction_result, device_result, graph_result,
        formula_score, transaction_data,
    )
    meta_result = await _call_agent_safe(meta_scorer_agent, meta_input, "MetaScorer")

    elapsed_ms = round((time.time() - start_time) * 1000, 1)

    # Save session to database for future behavioral comparison
    cumulative_score = meta_result.get("cumulative_fraud_score", formula_score)
    save_session(user_id, transaction_data, fraud_score=cumulative_score)

    # Build response
    return FraudAssessmentResponse(
        transaction_id=transaction_data.get("transaction_id", ""),
        user_id=user_id,
        behavioral=BehavioralAgentOutput(
            risk_score=scores["behavioral"],
            confidence=behavioral_result.get("confidence", 0.0),
            flags=behavioral_result.get("flags", []),
            reasoning=behavioral_result.get("reasoning", ""),
        ),
        cognitive=CognitiveAgentOutput(
            cognitive_risk_score=scores["cognitive"],
            confidence=cognitive_result.get("confidence", 0.0),
            detected_state=cognitive_result.get("detected_state", "normal"),
            coercion_indicators=cognitive_result.get("coercion_indicators", []),
            stress_indicators=cognitive_result.get("stress_indicators", []),
            coached_indicators=cognitive_result.get("coached_indicators", []),
            reasoning=cognitive_result.get("reasoning", ""),
        ),
        transaction=TransactionAgentOutput(
            risk_score=scores["transaction"],
            confidence=transaction_result.get("confidence", 0.0),
            flags=transaction_result.get("flags", []),
            reasoning=transaction_result.get("reasoning", ""),
        ),
        device=DeviceAgentOutput(
            risk_score=scores["device"],
            confidence=device_result.get("confidence", 0.0),
            flags=device_result.get("flags", []),
            reasoning=device_result.get("reasoning", ""),
        ),
        graph=GraphAgentOutput(
            risk_score=scores["graph"],
            confidence=graph_result.get("confidence", 0.0),
            flags=graph_result.get("flags", []),
            reasoning=graph_result.get("reasoning", ""),
        ),
        meta=MetaScorerOutput(
            cumulative_fraud_score=meta_result.get("cumulative_fraud_score", formula_score),
            risk_level=meta_result.get("risk_level", "low"),
            recommended_action=meta_result.get("recommended_action", "allow"),
            fraud_type_assessment=FraudTypeAssessment(**meta_result.get("fraud_type_assessment", {})),
            reasoning=meta_result.get("reasoning", ""),
            recommended_actions=meta_result.get("recommended_actions", []),
            agent_summary=meta_result.get("agent_summary", {}),
        ),
        processing_time_ms=elapsed_ms,
    )
