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


@router.get("/alerts")
async def list_alerts(unread_only: bool = False):
    """List alerts/notifications."""
    return store.get_alerts(unread_only)


@router.patch("/alerts/{alert_id}/read")
async def mark_read(alert_id: str):
    """Mark an alert as read."""
    ok = store.mark_alert_read(alert_id)
    return {"success": ok}


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
        "- Use short paragraphs separated by blank lines\n"
        "- Keep responses concise — 3-5 short paragraphs max\n"
        "- Reference specific numbers and scores inline"
    )

    messages = body.history + [{"role": "user", "content": body.question}]

    response = client.messages.create(
        model=settings.CHAT_MODEL_NAME,
        max_tokens=1024,
        system=system,
        messages=messages,
    )

    return {"response": response.content[0].text}
