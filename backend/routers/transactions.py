"""Transaction endpoints — submit transactions for fraud analysis."""

import uuid
from fastapi import APIRouter

from models.schemas import TransactionCreate, FraudAssessmentResponse
from agents.orchestrator import analyze_transaction

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.post("/", response_model=dict)
async def submit_transaction(tx: TransactionCreate):
    """Submit a transaction with behavioral telemetry for fraud analysis.

    Triggers the full multi-agent pipeline and returns the fraud assessment.
    """
    transaction_data = tx.model_dump()
    transaction_data["transaction_id"] = str(uuid.uuid4())

    # Convert enum values to strings
    transaction_data["transaction_type"] = tx.transaction_type.value
    transaction_data["auth_method"] = tx.auth_method.value

    result = await analyze_transaction(transaction_data)

    return {
        "transaction_id": transaction_data["transaction_id"],
        "assessment": result.model_dump(),
    }
