"""Transaction endpoints — submit transactions for fraud analysis."""

import uuid
from fastapi import APIRouter

from models.schemas import TransactionCreate
from agents.orchestrator import analyze_transaction
from seed.seed_scenarios import USER_BASELINES
import store

router = APIRouter(prefix="/api/transactions", tags=["transactions"])

USER_NAMES = {uid: b["name"] for uid, b in USER_BASELINES.items()}


@router.post("/", response_model=dict)
async def submit_transaction(tx: TransactionCreate):
    """Submit a transaction with behavioral telemetry for fraud analysis."""
    transaction_data = tx.model_dump()
    transaction_data["transaction_id"] = str(uuid.uuid4())
    transaction_data["transaction_type"] = tx.transaction_type.value
    transaction_data["auth_method"] = tx.auth_method.value

    user_id = tx.user_id
    user_name = USER_NAMES.get(user_id, user_id)
    pending_id = str(uuid.uuid4())

    # Create pending card on dashboard immediately
    store.save_pending_assessment(pending_id, user_id, user_name, "outgoing")
    await store.broadcast({
        "type": "analysis_started",
        "data": {"id": pending_id, "user_id": user_id, "user_name": user_name},
    })

    async def on_agent_complete(agent_name: str, score: int, confidence: float):
        await store.broadcast({
            "type": "agent_complete",
            "data": {"id": pending_id, "agent": agent_name, "score": score, "confidence": confidence},
        })

    result = await analyze_transaction(transaction_data, progress_callback=on_agent_complete)
    result_dict = result.model_dump()

    # Finalize: remove pending, save real assessment
    store.remove_pending(pending_id)
    entry = store.save_assessment(user_id, user_name, result_dict, transaction_direction="outgoing")
    await store.broadcast({
        "type": "analysis_complete",
        "data": {"pending_id": pending_id, "entry": entry},
    })

    return {
        "transaction_id": transaction_data["transaction_id"],
        "assessment": result_dict,
    }
