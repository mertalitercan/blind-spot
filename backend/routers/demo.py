"""Demo scenario endpoints — trigger pre-built fraud scenarios for testing."""

import uuid
from fastapi import APIRouter

from agents.orchestrator import analyze_transaction
from seed.seed_scenarios import get_scenario

router = APIRouter(prefix="/api/demo", tags=["demo"])


@router.post("/scenario/{scenario_name}")
async def run_demo_scenario(scenario_name: str):
    """Run a pre-built demo scenario through the full fraud detection pipeline.

    Available scenarios: normal, app_fraud, account_takeover, mule_network
    """
    scenario = get_scenario(scenario_name)
    transaction_data = scenario["transaction"]
    transaction_data["transaction_id"] = str(uuid.uuid4())

    result = await analyze_transaction(transaction_data)

    return {
        "scenario": scenario_name,
        "description": scenario["description"],
        "assessment": result.model_dump(),
    }


@router.get("/scenarios")
async def list_scenarios():
    """List available demo scenarios."""
    from seed.seed_scenarios import DEMO_SCENARIOS
    return {
        name: {"description": s["description"]}
        for name, s in DEMO_SCENARIOS.items()
    }
