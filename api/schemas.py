"""Pydantic schemas for API (no self-attestation fields)."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum


class SourceTypeAPI(str, Enum):
    USER_INPUT = "user_input"
    BLOCKCHAIN_TX = "blockchain_tx"
    API_RESPONSE = "api_response"
    SIGNED_ATTESTATION = "signed_attestation"
    OTHER = "other"


class ActionTypeAPI(str, Enum):
    TRANSFER = "TRANSFER"
    QUERY = "QUERY"
    SIGN = "SIGN"
    EXECUTE = "EXECUTE"
    OTHER = "other"


class DecisionAPI(str, Enum):
    ALLOWED = "ALLOWED"
    REVIEW = "REVIEW"
    DENIED = "DENIED"


class ReasoningStepAPI(BaseModel):
    """A single step in the agent's reasoning chain."""
    text: str
    source_type: SourceTypeAPI
    action_type: ActionTypeAPI
    source_reference: Optional[str] = None


class ContextAPI(BaseModel):
    """External context for verification."""
    kyc_verified: bool = False
    daily_limit_used: float = 0.0
    daily_limit_total: float = 10000.0
    sanctions_check_passed: bool = True
    custom_rules: Dict[str, bool] = Field(default_factory=dict)


class VerificationRequestAPI(BaseModel):
    """Request to verify an agent's intended action.

    IMPORTANT: No field for agent self-reported confidence.
    Trust is computed, not claimed.
    """
    reasoning_chain: List[ReasoningStepAPI]
    context: ContextAPI = Field(default_factory=ContextAPI)
    proposed_action: ActionTypeAPI


class TruthVectorAPI(BaseModel):
    """Four-dimensional trust metric."""
    anchor_integrity: float
    dependency_validity: float
    policy_compliance: float
    adversarial_risk: float


class VerificationResponseAPI(BaseModel):
    """Response from epistemic verification."""
    decision: DecisionAPI
    trust_score: float
    truth_vector: TruthVectorAPI
    trace_id: str
    reason: str
