"""Dataclasses and enums for Phase 1. No self-attestation fields."""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from datetime import datetime


class VerificationDecision(Enum):
    ALLOWED = "ALLOWED"
    REVIEW = "REVIEW"
    DENIED = "DENIED"


class SourceType(Enum):
    USER_INPUT = "user_input"
    BLOCKCHAIN_TX = "blockchain_tx"
    API_RESPONSE = "api_response"
    SIGNED_ATTESTATION = "signed_attestation"
    OTHER = "other"


class ActionType(Enum):
    TRANSFER = "TRANSFER"
    QUERY = "QUERY"
    SIGN = "SIGN"
    EXECUTE = "EXECUTE"
    OTHER = "other"


@dataclass
class ReasoningStep:
    """A single step in the agent's reasoning chain."""
    text: str
    source_type: SourceType
    action_type: ActionType
    timestamp: float = field(default_factory=datetime.now().timestamp)
    source_reference: Optional[str] = None  # e.g., tx_hash, API endpoint


@dataclass
class Context:
    """External context for verification (KYC status, limits, etc.)."""
    kyc_verified: bool = False
    daily_limit_used: float = 0.0
    daily_limit_total: float = 10000.0
    sanctions_check_passed: bool = True
    custom_rules: dict = field(default_factory=dict)


@dataclass
class TruthVector:
    """Four-dimensional trust metric. Computed by structural gate, not by agent."""
    anchor_integrity: float      # 0-1: do steps reference verifiable sources?
    dependency_validity: float   # 0-1: is the reasoning graph acyclic and sound?
    policy_compliance: float     # 0-1: do all steps comply with hard rules?
    adversarial_risk: float      # 0-1: probability of attack (higher = riskier)

    def __post_init__(self):
        """Clamp all values to [0, 1]."""
        for field_name in ["anchor_integrity", "dependency_validity", "policy_compliance", "adversarial_risk"]:
            value = getattr(self, field_name)
            setattr(self, field_name, max(0.0, min(1.0, value)))


@dataclass
class VerificationRequest:
    """Request to verify an agent's intended action.

    IMPORTANT: No field for agent self-reported confidence.
    Trust is computed, not claimed.
    """
    reasoning_chain: List[ReasoningStep]
    context: Context
    proposed_action: ActionType


@dataclass
class VerificationResult:
    """Result of epistemic verification."""
    decision: VerificationDecision
    trust_score: float  # 0-1, computed as average of TruthVector components (excluding adversarial_risk invert)
    truth_vector: TruthVector
    trace_id: str  # SHA-256 of (reasoning_chain, context, truth_vector, decision)
    reason: str
    timestamp: float = field(default_factory=datetime.now().timestamp)
