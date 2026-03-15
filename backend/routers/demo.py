"""Demo scenario endpoints — trigger pre-built fraud scenarios for testing."""

import uuid
from fastapi import APIRouter, HTTPException

from agents.orchestrator import analyze_transaction
from seed.seed_scenarios import get_scenario, USER_BASELINES, generate_dynamic_scenario
import store

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

    result = await analyze_transaction(transaction_data)
    result_dict = result.model_dump()

    # Save to store and broadcast to dashboard
    user_id = transaction_data.get("user_id", "unknown")
    user_name = USER_NAMES.get(user_id, user_id)
    direction = scenario.get("transaction_direction", "outgoing")
    entry = store.save_assessment(user_id, user_name, result_dict, transaction_direction=direction)
    await store.broadcast({
        "type": "new_assessment",
        "data": entry,
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

    result = await analyze_transaction(transaction_data)
    result_dict = result.model_dump()

    user_name = USER_NAMES.get(user_id, user_id)
    direction = scenario.get("transaction_direction", "incoming")
    entry = store.save_assessment(user_id, user_name, result_dict, transaction_direction=direction)
    await store.broadcast({"type": "new_assessment", "data": entry})

    return {
        "scenario": f"dynamic_{scenario_type}",
        "description": scenario["description"],
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
