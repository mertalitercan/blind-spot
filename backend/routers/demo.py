"""Demo scenario endpoints — trigger pre-built fraud scenarios for testing."""

import json
import time
import uuid
import anthropic
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config import Settings
from agents.orchestrator import analyze_transaction
from seed.seed_scenarios import (
    get_scenario, USER_BASELINES, generate_dynamic_scenario,
    SENDER_PROFILES, RECIPIENT_PROFILES_BUSINESS, _build_payload, _USER_DEVICES,
)
import store

settings = Settings()

router = APIRouter(prefix="/api/demo", tags=["demo"])

USER_NAMES = {uid: b["name"] for uid, b in USER_BASELINES.items()}


@router.post("/scenario/{scenario_name}")
async def run_demo_scenario(scenario_name: str):
    """Run a pre-built demo scenario through the full fraud detection pipeline.

    Available scenarios: normal, app_fraud, account_takeover, mule_network
    """
    scenario = get_scenario(scenario_name)
    transaction_data = scenario["transaction"]
    transaction_data["transaction_id"] = str(uuid.uuid4())

    user_id = transaction_data.get("user_id", "unknown")
    user_name = USER_NAMES.get(user_id, user_id)
    direction = scenario.get("transaction_direction", "outgoing")
    pending_id = str(uuid.uuid4())

    store.save_pending_assessment(pending_id, user_id, user_name, direction)
    await store.broadcast({
        "type": "analysis_started",
        "data": {"id": pending_id, "user_id": user_id, "user_name": user_name},
    })

    async def on_agent_complete(agent_name: str, score: int, confidence: float):
        await store.broadcast({
            "type": "agent_complete",
            "data": {"id": pending_id, "agent": agent_name, "score": score, "confidence": confidence},
        })

    t0 = time.time()
    result = await analyze_transaction(transaction_data, progress_callback=on_agent_complete)
    result_dict = result.model_dump()
    store.record_response_time(time.time() - t0)

    amount = transaction_data.get("amount", 0)
    store.remove_pending(pending_id)
    entry = store.save_assessment(user_id, user_name, result_dict, transaction_direction=direction, amount=amount)
    await store.broadcast({
        "type": "analysis_complete",
        "data": {"pending_id": pending_id, "entry": entry},
    })

    return {
        "scenario": scenario_name,
        "description": scenario["description"],
        "assessment": result_dict,
    }


@router.post("/generate/{user_id}/{scenario_type}")
async def generate_user_scenario(user_id: str, scenario_type: str):
    """Generate a dynamic scenario based on the logged-in user's baseline.

    scenario_type: 'safe' or 'suspicious'
    For suspicious: 2 out of 3 calls → MEDIUM risk, 1 out of 3 → HIGH risk.
    """
    if scenario_type not in ("safe", "suspicious"):
        raise HTTPException(status_code=400, detail="Type must be 'safe' or 'suspicious'")
    if user_id not in USER_BASELINES:
        raise HTTPException(status_code=404, detail=f"Unknown user: {user_id}")

    scenario = generate_dynamic_scenario(user_id, scenario_type)
    transaction_data = scenario["transaction"]
    transaction_data["transaction_id"] = str(uuid.uuid4())

    user_name = USER_NAMES.get(user_id, user_id)
    direction = scenario.get("transaction_direction", "incoming")
    pending_id = str(uuid.uuid4())

    store.save_pending_assessment(pending_id, user_id, user_name, direction)
    await store.broadcast({
        "type": "analysis_started",
        "data": {"id": pending_id, "user_id": user_id, "user_name": user_name},
    })

    async def on_agent_complete(agent_name: str, score: int, confidence: float):
        await store.broadcast({
            "type": "agent_complete",
            "data": {"id": pending_id, "agent": agent_name, "score": score, "confidence": confidence},
        })

    t0 = time.time()
    result = await analyze_transaction(transaction_data, progress_callback=on_agent_complete)
    result_dict = result.model_dump()
    store.record_response_time(time.time() - t0)

    amount = transaction_data.get("amount", 0)
    store.remove_pending(pending_id)
    entry = store.save_assessment(user_id, user_name, result_dict, transaction_direction=direction, amount=amount)
    await store.broadcast({
        "type": "analysis_complete",
        "data": {"pending_id": pending_id, "entry": entry},
    })

    return {
        "scenario": f"dynamic_{scenario_type}",
        "description": scenario["description"],
        "assessment": result_dict,
    }


class CustomPromptRequest(BaseModel):
    prompt: str


@router.post("/generate-custom/{user_id}")
async def generate_custom_scenario(user_id: str, body: CustomPromptRequest):
    """Generate a scenario from a natural language prompt using AI.

    The AI receives the user's baseline profile and generates realistic
    transaction parameters matching the described situation.
    """
    if user_id not in USER_BASELINES:
        raise HTTPException(status_code=404, detail=f"Unknown user: {user_id}")

    baseline = USER_BASELINES[user_id]
    sender = SENDER_PROFILES.get(user_id, {})
    loc = sender.get("typical_location", {"city": "Toronto", "country": "CA", "lat": 43.65, "lng": -79.38})
    device = _USER_DEVICES.get(user_id, _USER_DEVICES["ediz-uysal"])

    # Build the AI prompt
    system_prompt = (
        "You generate realistic transaction parameters for a fraud detection demo. "
        "Given a user's baseline behavior and a scenario description, output a JSON object "
        "with the exact keys listed below. Output ONLY valid JSON, no markdown, no explanation.\n\n"
        f"USER BASELINE:\n{json.dumps(baseline, indent=2, default=str)}\n\n"
        f"USER PROFILE:\n{json.dumps(sender, indent=2)}\n\n"
        f"AVAILABLE RECIPIENTS: {json.dumps(list(RECIPIENT_PROFILES_BUSINESS.keys()))}\n\n"
        "RULES:\n"
        "- recipient_id MUST be picked from the AVAILABLE RECIPIENTS list above. Do NOT invent new ones.\n"
        "- For suspicious scenarios, use recipients like CA-9284710-JS, CA-7731205-QC, "
        "KY-8850134-OH, or DE-4419823-ET.\n"
        "- For safe scenarios, use recipients like landlord-utilities, grocery-store, pharmacy, or friend-alex-890.\n"
        "- description must be SHORT (max 10 words), e.g. 'Coerced transfer while on phone call'\n"
        "- Keep amounts realistic relative to the user's monthly income range.\n\n"
        "OUTPUT FORMAT — return a JSON object with these exact keys:\n"
        "{\n"
        '  "recipient_id": "string — MUST be from the available recipients list",\n'
        '  "amount": number,\n'
        '  "typing_speed": number (wpm),\n'
        '  "error_rate": number (0.0-0.2),\n'
        '  "pressure": number (0.3-0.8),\n'
        '  "radius": number (8-20),\n'
        '  "directness": number (0.1-0.95),\n'
        '  "session_dur": number (ms, 30000-600000),\n'
        '  "hesitation": number (ms, 50-15000),\n'
        '  "confirm_attempts": number (1-5),\n'
        '  "auth": "biometric" or "password" or "password_reset",\n'
        '  "hour": number (0-23),\n'
        '  "paste": boolean,\n'
        '  "paste_field": "" or "recipient_account" or "amount",\n'
        '  "segmented": boolean,\n'
        '  "phone_call": boolean,\n'
        '  "phone_dur": number (ms, 0-900000),\n'
        '  "is_vpn": boolean,\n'
        '  "is_emulator": boolean,\n'
        '  "is_rooted": boolean,\n'
        '  "familiarity": number (0.1-0.95),\n'
        '  "dead_time": number (ms, 0-60000),\n'
        '  "description": "SHORT max 10 words describing the scenario"\n'
        "}\n\n"
        "Make the parameters REALISTIC for the described scenario. "
        "If the scenario describes fraud/scam, make behavioral signals suspicious (slow typing, "
        "high hesitation, phone call active, paste used, etc). "
        "If it describes normal activity, keep signals matching the baseline."
    )

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=settings.CHAT_MODEL_NAME,
        max_tokens=800,
        system=system_prompt,
        messages=[{"role": "user", "content": body.prompt}],
    )

    # Parse Claude's JSON response
    raw = response.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3].strip()

    try:
        params = json.loads(raw)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI returned invalid JSON")

    description = params.pop("description", body.prompt)

    # Generate rhythm from baseline
    base_rhythm = baseline.get("typing_rhythm_signature", [100]*10)
    import random
    rhythm = [max(20, r + random.randint(-15, 15)) for r in base_rhythm]

    # Build the transaction payload
    ip_range = baseline.get("typical_ip_range", "24.114.x.x")
    parts = ip_range.split(".")
    ip = f"{parts[0]}.{parts[1]}.{random.randint(1,254)}.{random.randint(1,254)}"

    ip_loc = loc.copy()
    if params.get("is_vpn"):
        ip_loc = {"city": "Berlin", "country": "DE", "lat": 52.52, "lng": 13.41}

    transaction_data = _build_payload(
        user_id=user_id,
        baseline=baseline,
        loc=loc,
        device=device,
        recipient_id=params.get("recipient_id", "landlord-utilities"),
        amount=params.get("amount", 100.0),
        typing_speed=params.get("typing_speed", baseline.get("avg_typing_speed_wpm", 40)),
        error_rate=params.get("error_rate", 0.02),
        rhythm=rhythm,
        pressure=params.get("pressure", 0.5),
        radius=params.get("radius", 12.0),
        hand=baseline.get("hand_dominance", "right"),
        directness=params.get("directness", 0.5),
        session_dur=params.get("session_dur", 120000),
        hesitation=params.get("hesitation", 200),
        confirm_attempts=params.get("confirm_attempts", 1),
        ip=ip,
        ip_loc=ip_loc,
        auth=params.get("auth", "biometric"),
        hour=params.get("hour", 14),
        paste=params.get("paste", False),
        paste_field=params.get("paste_field", ""),
        segmented=params.get("segmented", False),
        phone_call=params.get("phone_call", False),
        phone_dur=params.get("phone_dur", 0),
        is_vpn=params.get("is_vpn", False),
        is_emulator=params.get("is_emulator", False),
        is_rooted=params.get("is_rooted", False),
        familiarity=params.get("familiarity", 0.7),
        dead_time=params.get("dead_time", 0),
    )
    transaction_data["transaction_id"] = str(uuid.uuid4())

    user_name = USER_NAMES.get(user_id, user_id)
    direction = "incoming"
    pending_id = str(uuid.uuid4())

    store.save_pending_assessment(pending_id, user_id, user_name, direction)
    await store.broadcast({
        "type": "analysis_started",
        "data": {"id": pending_id, "user_id": user_id, "user_name": user_name},
    })

    async def on_agent_complete(agent_name: str, score: int, confidence: float):
        await store.broadcast({
            "type": "agent_complete",
            "data": {"id": pending_id, "agent": agent_name, "score": score, "confidence": confidence},
        })

    t0 = time.time()
    result = await analyze_transaction(transaction_data, progress_callback=on_agent_complete)
    result_dict = result.model_dump()
    store.record_response_time(time.time() - t0)

    amount = transaction_data.get("amount", 0)
    store.remove_pending(pending_id)
    entry = store.save_assessment(user_id, user_name, result_dict, transaction_direction=direction, amount=amount)
    await store.broadcast({
        "type": "analysis_complete",
        "data": {"pending_id": pending_id, "entry": entry},
    })

    return {
        "scenario": "custom_prompt",
        "description": description,
        "assessment": result_dict,
    }


@router.get("/scenarios")
async def list_scenarios():
    """List available demo scenarios."""
    from seed.seed_scenarios import DEMO_SCENARIOS
    return {
        name: {"description": s["description"]}
        for name, s in DEMO_SCENARIOS.items()
    }
