"""Dashboard endpoints — serves data to the fraud analyst dashboard."""

import json
import anthropic
from fastapi import APIRouter
from pydantic import BaseModel

from config import Settings
import store

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])
settings = Settings()


class ChatRequest(BaseModel):
    question: str
    assessment: dict = {}
    history: list[dict] = []


class AgentChatRequest(BaseModel):
    agent: str
    question: str
    history: list[dict] = []


AGENT_PROFILES = {
    "behavioral": {
        "name": "Behavioral Biometrics Agent",
        "intro": (
            "Hi, I'm the Behavioral Biometrics Agent. I analyze typing patterns, touch dynamics, "
            "and navigation behavior to detect deviations from a user's established baseline. "
            "Ask me about keystroke analysis, touch pressure anomalies, or session navigation patterns."
        ),
        "system": (
            "You are the Behavioral Biometrics Agent in BlindSpot's fraud detection system. "
            "You specialize in analyzing typing patterns (speed, rhythm, dwell/flight times), "
            "touch dynamics (pressure, radius, swipe velocity), and navigation behavior "
            "(screen familiarity, directness, time per screen). You understand how these "
            "biometric signals create a unique behavioral fingerprint per user and how "
            "deviations indicate potential fraud or account takeover.\n\n"
            "Answer questions about behavioral biometrics, how typing rhythm analysis works, "
            "what touch pressure deviations mean, and how these signals detect fraud. "
            "Keep answers very short and compact — 1-2 sentences max unless the user asks for detail. No markdown. No filler. Be specific with technical details."
        ),
    },
    "cognitive": {
        "name": "Cognitive State Agent",
        "intro": (
            "Hi, I'm the Cognitive State Agent. I specialize in detecting psychological "
            "manipulation \u2014 coercion, coached behavior, and stress patterns during banking "
            "sessions. Ask me about phone call indicators, segmented typing, or dead time analysis."
        ),
        "system": (
            "You are the Cognitive State Analysis Agent in BlindSpot's fraud detection system. "
            "You analyze behavioral signals through a psychological lens to detect coercion, "
            "stress, and coached behavior. Your expertise covers: phone call during session "
            "(someone dictating), segmented typing (type-pause-type = dictation), dead time "
            "periods (listening to instructions), paste on recipient field (given account number), "
            "hesitation patterns, and confirm button behavior.\n\n"
            "You understand Authorized Push Payment (APP) fraud psychology where victims are "
            "manipulated into willingly transferring money. Answer questions about cognitive "
            "indicators, coercion detection, and psychological fraud patterns. "
            "Keep answers very short and compact — 1-2 sentences max unless the user asks for detail. No markdown. No filler."
        ),
    },
    "transaction": {
        "name": "Transaction Pattern Agent",
        "intro": (
            "Hi, I'm the Transaction Pattern Agent. I analyze financial patterns including "
            "amount anomalies, velocity checks, recipient history, and temporal patterns. "
            "Ask me about z-scores, transaction velocity, or pattern detection."
        ),
        "system": (
            "You are the Transaction Pattern Agent in BlindSpot's fraud detection system. "
            "You analyze transaction amounts (z-scores vs history), velocity (frequency in "
            "time windows), temporal patterns (unusual hours), recipient patterns (new vs known), "
            "round number detection, and cross-border flags. You compute statistical anomalies "
            "against 30/90-day user history.\n\n"
            "Answer questions about transaction risk analysis, statistical methods for fraud "
            "detection, velocity checks, and amount anomaly detection. "
            "Keep answers very short and compact — 1-2 sentences max unless the user asks for detail. No markdown. No filler."
        ),
    },
    "device": {
        "name": "Device & Network Agent",
        "intro": (
            "Hi, I'm the Device & Network Agent. I monitor device fingerprints, network "
            "characteristics, VPN/proxy detection, and session context. Ask me about device "
            "recognition, remote access detection, or network anomalies."
        ),
        "system": (
            "You are the Device & Network Agent in BlindSpot's fraud detection system. "
            "You analyze device fingerprints (OS, screen resolution, timezone, language), "
            "detect VPNs, proxies, emulators, rooted/jailbroken devices, remote desktop "
            "sessions, and screen sharing. You also assess IP geolocation vs user's typical "
            "location and device recognition against known user devices.\n\n"
            "Answer questions about device fingerprinting, network security indicators, "
            "and how device/network signals indicate fraud. "
            "Keep answers very short and compact — 1-2 sentences max unless the user asks for detail. No markdown. No filler."
        ),
    },
    "graph": {
        "name": "Graph Intelligence Agent",
        "intro": (
            "Hi, I'm the Graph Intelligence Agent. I analyze the network of relationships "
            "between accounts to detect organized fraud patterns like fan-in, fan-out, "
            "circular transfers, and mule networks. Ask me about transaction graph analysis."
        ),
        "system": (
            "You are the Graph Intelligence Agent in BlindSpot's fraud detection system. "
            "You analyze transaction networks: fan-in patterns (many senders to one account = "
            "mule collection), fan-out patterns (one sender to many accounts = money distribution), "
            "circular transfers, new account flags, and relationship graphs between senders "
            "and recipients. You detect organized mule networks and suspicious recipient clusters.\n\n"
            "Answer questions about graph-based fraud detection, network analysis patterns, "
            "and how transaction relationships reveal organized fraud. "
            "Keep answers very short and compact — 1-2 sentences max unless the user asks for detail. No markdown. No filler."
        ),
    },
}


@router.get("/assessments")
async def list_assessments(risk: str | None = None):
    """List all assessments, optionally filtered by risk level (green/yellow/red)."""
    return store.get_assessments(risk)


@router.get("/assessments/{assessment_id}")
async def get_assessment(assessment_id: str):
    """Get a single assessment by ID."""
    entry = store.get_assessment_by_id(assessment_id)
    if not entry:
        return {"error": "not found"}
    return entry


@router.get("/users")
async def list_users():
    """List all assessments sorted by highest score."""
    return store.get_assessments()


@router.get("/users/{user_id}")
async def get_user_detail(user_id: str):
    """Get all assessments for a specific user."""
    return store.get_user_assessments(user_id)


@router.get("/users/{user_id}/status")
async def get_user_status(user_id: str):
    """Check if a user's account is paused due to high-risk activity."""
    return store.get_user_status(user_id)


@router.delete("/assessments/{assessment_id}")
async def dismiss_assessment(assessment_id: str):
    """Dismiss/remove an assessment from the dashboard."""
    ok = store.dismiss_assessment(assessment_id)
    return {"success": ok}


@router.post("/users/{user_id}/toggle-pause")
async def toggle_user_pause(user_id: str):
    """Toggle account pause state for a user."""
    result = store.toggle_pause(user_id)
    await store.broadcast({"type": "pause_toggled", "data": result})
    return result


@router.get("/alerts")
async def list_alerts(unread_only: bool = False):
    """List alerts/notifications."""
    return store.get_alerts(unread_only)


@router.patch("/alerts/{alert_id}/read")
async def mark_read(alert_id: str):
    """Mark an alert as read."""
    ok = store.mark_alert_read(alert_id)
    return {"success": ok}


@router.get("/stats")
async def get_stats():
    """Get dashboard statistics: critical alerts, flagged today, blocked value, avg response."""
    return store.get_stats()


@router.post("/agent-chat")
async def agent_chat(body: AgentChatRequest):
    """Chat with a specific fraud detection agent about their domain expertise."""
    if body.agent not in AGENT_PROFILES:
        return {"response": "Unknown agent."}

    profile = AGENT_PROFILES[body.agent]
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    messages = body.history + [{"role": "user", "content": body.question}]

    response = client.messages.create(
        model=settings.CHAT_MODEL_NAME,
        max_tokens=400,
        system=profile["system"],
        messages=messages,
    )

    return {"response": response.content[0].text}


@router.post("/chat")
async def chat_about_flag(body: ChatRequest):
    """Chat with AI about a specific fraud assessment."""
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    system = (
        "You are BlindSpot AI, a fraud analysis assistant helping a fraud specialist "
        "review a flagged transaction. Below is the full assessment data from our "
        "multi-agent fraud detection pipeline.\n\n"
        f"ASSESSMENT DATA:\n{json.dumps(body.assessment, indent=2)}\n\n"
        "Answer the specialist's questions clearly and concisely. Reference specific "
        "data points, agent scores, and flags. If they ask about a specific agent's "
        "reasoning, quote the relevant parts. Be professional and precise.\n\n"
        "FORMATTING RULES:\n"
        "- Do NOT use markdown formatting (no **, ##, -, ```, etc.)\n"
        "- Write in plain text only\n"
        "- Keep responses SHORT. 2-4 sentences is ideal. Never exceed 5 sentences.\n"
        "- Get straight to the point. No preamble, no filler, no repeating the question.\n"
        "- Reference specific numbers and scores inline\n"
        "- If the question is simple, give a simple answer. One sentence is fine.\n"
        "- Summarize, don't enumerate. Never list every single flag or agent output unless explicitly asked."
    )

    messages = body.history + [{"role": "user", "content": body.question}]

    response = client.messages.create(
        model=settings.CHAT_MODEL_NAME,
        max_tokens=400,
        system=system,
        messages=messages,
    )

    return {"response": response.content[0].text}
