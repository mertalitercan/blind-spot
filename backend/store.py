"""In-memory store for fraud assessments, alerts, and WebSocket connections."""

import json
import uuid
from datetime import datetime, timezone, date

assessments: list[dict] = []
alerts: list[dict] = []
pending_assessments: dict[str, dict] = {}
dismissed_ids: set[str] = set()
paused_overrides: dict[str, bool] = {}  # user_id -> manual pause state
websocket_connections: set = set()
response_times: list[float] = []  # seconds per analysis


def risk_level_from_score(score: int) -> str:
    if score >= 71:
        return "red"
    if score >= 31:
        return "yellow"
    return "green"


def save_assessment(user_id: str, user_name: str, result: dict, transaction_direction: str = "outgoing", amount: float = 0.0) -> dict:
    meta = result.get("meta", {})
    score = meta.get("cumulative_fraud_score", 0)
    risk = risk_level_from_score(score)

    entry = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "user_name": user_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cumulative_fraud_score": score,
        "risk_level": risk,
        "transaction_direction": transaction_direction,
        "amount": amount,
        "assessment": result,
    }
    assessments.append(entry)

    # Auto-create alert for medium+ risk
    if score >= 31:
        direction_label = "incoming" if transaction_direction == "incoming" else "outgoing"
        alert = {
            "id": str(uuid.uuid4()),
            "assessment_id": entry["id"],
            "user_id": user_id,
            "user_name": user_name,
            "score": score,
            "risk_level": risk,
            "message": f"{'High' if score >= 71 else 'Medium'} risk {direction_label} transaction detected for {user_name} (score: {score}/100)",
            "timestamp": entry["timestamp"],
            "read": False,
        }
        alerts.append(alert)

    # Auto-pause account for high risk
    if score >= 71:
        paused_overrides[user_id] = True

    return entry


def save_pending_assessment(pending_id: str, user_id: str, user_name: str, direction: str = "outgoing"):
    """Create a placeholder assessment while agents are running."""
    pending_assessments[pending_id] = {
        "id": pending_id,
        "user_id": user_id,
        "user_name": user_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "transaction_direction": direction,
        "status": "processing",
    }


def remove_pending(pending_id: str):
    """Remove a pending assessment after it's finalized."""
    pending_assessments.pop(pending_id, None)


def dismiss_assessment(assessment_id: str) -> bool:
    """Dismiss an assessment from the dashboard view."""
    for a in assessments:
        if a["id"] == assessment_id:
            dismissed_ids.add(assessment_id)
            return True
    return False


def toggle_pause(user_id: str) -> dict:
    """Toggle the pause state for a user. Returns the new state."""
    current = is_user_paused(user_id)
    paused_overrides[user_id] = not current
    return {"user_id": user_id, "paused": not current}


def is_user_paused(user_id: str) -> bool:
    """Check if a user is paused (manual override or auto from score)."""
    if user_id in paused_overrides:
        return paused_overrides[user_id]
    # Auto-pause: latest assessment score >= 71
    user_assessments = [a for a in assessments if a["user_id"] == user_id and a["id"] not in dismissed_ids]
    if not user_assessments:
        return False
    latest = max(user_assessments, key=lambda x: x["timestamp"])
    return latest["cumulative_fraud_score"] >= 71


def get_assessments(risk: str | None = None) -> list[dict]:
    items = [a for a in assessments if a["id"] not in dismissed_ids]
    if risk:
        items = [a for a in items if a["risk_level"] == risk]
    result = sorted(items, key=lambda x: x["cumulative_fraud_score"], reverse=True)
    # Attach current pause state per user
    for item in result:
        item["paused"] = is_user_paused(item["user_id"])
    return result


def get_assessment_by_id(assessment_id: str) -> dict | None:
    for a in assessments:
        if a["id"] == assessment_id:
            return a
    return None


def get_users_summary() -> list[dict]:
    """Get latest assessment per user, sorted by highest score."""
    latest: dict[str, dict] = {}
    for a in assessments:
        uid = a["user_id"]
        if uid not in latest or a["timestamp"] > latest[uid]["timestamp"]:
            latest[uid] = a
    return sorted(latest.values(), key=lambda x: x["cumulative_fraud_score"], reverse=True)


def get_user_assessments(user_id: str) -> list[dict]:
    return sorted(
        [a for a in assessments if a["user_id"] == user_id],
        key=lambda x: x["timestamp"],
        reverse=True,
    )


def get_user_status(user_id: str) -> dict:
    """Check if a user's account is paused."""
    paused = is_user_paused(user_id)
    if not paused:
        return {"paused": False, "reason": ""}
    user_assessments = [a for a in assessments if a["user_id"] == user_id]
    if user_assessments:
        latest = max(user_assessments, key=lambda x: x["timestamp"])
        score = latest.get("cumulative_fraud_score", 0)
        risk = latest.get("risk_level", "unknown")
        if risk == "red":
            reason = "Suspicious activity was detected on your account. Your account has been temporarily frozen for your protection."
        else:
            reason = "Unusual activity was detected on your account. Your account has been temporarily paused for review."
        return {"paused": True, "reason": reason}
    return {"paused": True, "reason": "Your account has been temporarily paused due to unusual activity."}


def get_alerts(unread_only: bool = False) -> list[dict]:
    items = alerts
    if unread_only:
        items = [a for a in items if not a["read"]]
    return sorted(items, key=lambda x: x["timestamp"], reverse=True)


def mark_alert_read(alert_id: str) -> bool:
    for a in alerts:
        if a["id"] == alert_id:
            a["read"] = True
            return True
    return False


def record_response_time(seconds: float):
    """Record how long an analysis took."""
    response_times.append(seconds)


def get_stats() -> dict:
    """Compute dashboard stats: critical alerts, flagged today, blocked value, avg response."""
    today_str = date.today().isoformat()

    critical_count = len([a for a in alerts if a["risk_level"] == "red"])
    flagged_today = len([
        a for a in assessments
        if a["id"] not in dismissed_ids
        and a["risk_level"] in ("red", "yellow")
        and a["timestamp"][:10] == today_str
    ])
    blocked_value = sum(
        a.get("amount", 0)
        for a in assessments
        if a["id"] not in dismissed_ids and is_user_paused(a["user_id"])
    )
    accounts_paused = len(set(
        a["user_id"] for a in assessments
        if a["id"] not in dismissed_ids and is_user_paused(a["user_id"])
    ))

    return {
        "critical_alerts": critical_count,
        "flagged_today": flagged_today,
        "blocked_value": round(blocked_value, 2),
        "accounts_paused": accounts_paused,
    }


async def broadcast(message: dict):
    for ws in list(websocket_connections):
        try:
            await ws.send_json(message)
        except Exception:
            websocket_connections.discard(ws)
