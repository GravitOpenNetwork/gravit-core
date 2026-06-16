"""Orchestrator — combines structural gate, advisory layer, and audit proof."""
from .schemas import VerificationRequest, VerificationResult
from .structural_gate import StructuralGate
from .advisory_layer import AdvisoryLayer, NullAdvisoryLayer
from .audit_proof import AuditProof


class EpistemicVerifierPhase1:
    def __init__(self, structural_gate: StructuralGate = None, advisory_layer: AdvisoryLayer = None):
        self.structural_gate = structural_gate or StructuralGate()
        self.advisory_layer = advisory_layer or NullAdvisoryLayer()

    def verify(self, request: VerificationRequest) -> VerificationResult:
        truth_vector, decision, reason = self.structural_gate.compute(
            request.reasoning_chain, request.context
        )

        trust_score = (
            truth_vector.anchor_integrity +
            truth_vector.dependency_validity +
            truth_vector.policy_compliance
        ) / 3.0
        trust_score = trust_score * (1.0 - truth_vector.adversarial_risk * 0.5)

        result = VerificationResult(
            decision=decision,
            trust_score=trust_score,
            truth_vector=truth_vector,
            trace_id="",
            reason=reason
        )

        trace_id = AuditProof.compute_trace_id(request, result)
        result.trace_id = trace_id

        self.advisory_layer.advise(request, result)

        return result
