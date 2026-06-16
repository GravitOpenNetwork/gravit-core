"""Deterministic SHA-256 audit proof. Any third party can recompute."""
import hashlib
import json
from typing import List, Any
from .schemas import VerificationRequest, VerificationResult


class AuditProof:
    """Generates and verifies deterministic audit proofs."""

    @staticmethod
    def compute_trace_id(request: VerificationRequest, result: VerificationResult) -> str:
        """Compute SHA-256 hash over (reasoning_chain, context, truth_vector, decision).

        This is deterministic — any third party with the same inputs will get the same trace_id.
        """
        # Convert to serializable dicts
        data = {
            "reasoning_chain": [
                {
                    "text": step.text,
                    "source_type": step.source_type.value,
                    "action_type": step.action_type.value,
                    "timestamp": step.timestamp,
                    "source_reference": step.source_reference
                }
                for step in request.reasoning_chain
            ],
            "context": {
                "kyc_verified": request.context.kyc_verified,
                "daily_limit_used": request.context.daily_limit_used,
                "daily_limit_total": request.context.daily_limit_total,
                "sanctions_check_passed": request.context.sanctions_check_passed,
                "custom_rules": request.context.custom_rules
            },
            "truth_vector": {
                "anchor_integrity": result.truth_vector.anchor_integrity,
                "dependency_validity": result.truth_vector.dependency_validity,
                "policy_compliance": result.truth_vector.policy_compliance,
                "adversarial_risk": result.truth_vector.adversarial_risk
            },
            "decision": result.decision.value,
            "timestamp": result.timestamp
        }

        # Deterministic JSON serialization (sort_keys=True)
        json_str = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(json_str.encode()).hexdigest()

    @staticmethod
    def verify_trace_id(request: VerificationRequest, result: VerificationResult) -> bool:
        """Verify that the trace_id in result matches recomputed value."""
        expected = AuditProof.compute_trace_id(request, result)
        return expected == result.trace_id
