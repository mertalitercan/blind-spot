"""In-memory store for fraud assessments, alerts, and WebSocket connections."""

import json
import uuid
from datetime import datetime, timezone

assessments: list[dict] = []
alerts: list[dict] = []
websocket_connections: set = set()


def risk_level_from_score(score: int) -> str:
    if score >= 71:
        return "red"
    if score >= 31:
        return "yellow"
    return "green"


def save_assessment(user_id: str, user_name: str, result: dict, transaction_direction: str = "outgoing") -> dict:
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

    return entry


def get_assessments(risk: str | None = None) -> list[dict]:
    items = assessments
    if risk:
        items = [a for a in items if a["risk_level"] == risk]
    return sorted(items, key=lambda x: x["cumulative_fraud_score"], reverse=True)


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


async def broadcast(message: dict):
    for ws in list(websocket_connections):
        try:
            await ws.send_json(message)
        except Exception:
            websocket_connections.discard(ws)
