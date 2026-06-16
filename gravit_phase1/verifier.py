"""Orchestrator — combines structural gate, advisory layer, and audit proof."""
from .schemas import VerificationRequest, VerificationResult
from .structural_gate import StructuralGate
from .advisory_layer import AdvisoryLayer, NullAdvisoryLayer
from .audit_proof import AuditProof


class EpistemicVerifierPhase1:
    """Main verifier orchestrator."""

    def __init__(self, structural_gate: StructuralGate = None, advisory_layer: AdvisoryLayer = None):
        self.structural_gate = structural_gate or StructuralGate()
        self.advisory_layer = advisory_layer or NullAdvisoryLayer()

    def verify(self, request: VerificationRequest) -> VerificationResult:
        """Verify an agent's request. Returns decision + audit proof."""
        # 1. Structural gate computes decision (NO LLM INPUT)
        truth_vector, decision, reason = self.structural_gate.compute(
            request.reasoning_chain, request.context
        )

        # 2. Compute trust_score from truth_vector
        # trust_score = average of anchor, dependency, policy (adversarial is a risk factor)
        trust_score = (
            truth_vector.anchor_integrity +
            truth_vector.dependency_validity +
            truth_vector.policy_compliance
        ) / 3.0
        # Reduce by adversarial risk (but not below 0)
        trust_score = trust_score * (1.0 - truth_vector.adversarial_risk * 0.5)

        # 3. Create result (without advisory yet)
        result = VerificationResult(
            decision=decision,
            trust_score=trust_score,
            truth_vector=truth_vector,
            trace_id="",  # temporary, will compute after
            reason=reason,
            timestamp=0.0  # temporary
        )

        # 4. Compute deterministic trace_id (before advisory, because advisory doesn't affect decision)
        trace_id = AuditProof.compute_trace_id(request, result)
        result.trace_id = trace_id

        # 5. Advisory layer (optional, does NOT affect result fields)
        advisory_comment = self.advisory_layer.advise(request, result)
        # In a real system, you'd log advisory_comment. For now, ignore.

        return result
