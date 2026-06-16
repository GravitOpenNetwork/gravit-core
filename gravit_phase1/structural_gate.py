"""Structural Gate — the ONLY component that computes trust scores and decisions."""
from typing import List, Tuple
from .schemas import (
    TruthVector, VerificationDecision, Context, ReasoningStep,
    ActionType, SourceType
)


class StructuralGate:
    """Decisions are made here. No LLM, no agent self-report."""

    def compute(self, reasoning_chain: List[ReasoningStep], context: Context) -> Tuple[TruthVector, VerificationDecision, str]:
        """Returns (TruthVector, decision, reason) based ONLY on structure."""

        anchor_score = self._check_anchors(reasoning_chain)
        dep_score = self._check_dependencies(reasoning_chain)
        policy_violation, policy_reason = self._check_policies(reasoning_chain, context)

        if policy_violation:
            return (
                TruthVector(anchor_integrity=0, dependency_validity=0, policy_compliance=0, adversarial_risk=1.0),
                VerificationDecision.DENIED,
                f"Hard policy violation: {policy_reason}"
            )

        adv_risk = self._check_adversarial(reasoning_chain)

        trust_score = (anchor_score + dep_score + 1.0) / 3.0
        trust_score = trust_score * (1.0 - adv_risk * 0.5)

        truth_vector = TruthVector(
            anchor_integrity=anchor_score,
            dependency_validity=dep_score,
            policy_compliance=1.0,
            adversarial_risk=adv_risk
        )

        decision = VerificationDecision.ALLOWED if trust_score >= 0.7 else VerificationDecision.REVIEW

        return truth_vector, decision, f"trust_score={trust_score:.2f}"

    def _check_anchors(self, chain: List[ReasoningStep]) -> float:
        if not chain:
            return 0.0
        verified_sources = {SourceType.BLOCKCHAIN_TX, SourceType.API_RESPONSE, SourceType.SIGNED_ATTESTATION}
        verified = sum(1 for step in chain if step.source_type in verified_sources)
        return verified / len(chain)

    def _check_dependencies(self, chain: List[ReasoningStep]) -> float:
        if not chain:
            return 0.0
        has_refs = all(step.source_reference is not None for step in chain)
        return 1.0 if has_refs else 0.8

    def _check_policies(self, chain: List[ReasoningStep], context: Context) -> Tuple[bool, str]:
        has_transfer = any(step.action_type == ActionType.TRANSFER for step in chain)

        if has_transfer:
            if not context.kyc_verified:
                return True, "TRANSFER requires KYC verification"
            if context.daily_limit_used > context.daily_limit_total:
                return True, f"Daily limit exceeded"
            if not context.sanctions_check_passed:
                return True, "Sanctions check failed"

        for rule_name, rule_value in context.custom_rules.items():
            if not rule_value:
                return True, f"Custom policy violation: {rule_name}"

        return False, ""

    def _check_adversarial(self, chain: List[ReasoningStep]) -> float:
        risk = 0.0
        texts = [step.text for step in chain]
        if len(set(texts)) < len(texts):
            risk += 0.3
        if len(chain) < 2:
            risk += 0.2

        suspicious = ["ignore policy", "bypass", "override"]
        for step in chain:
            for sus in suspicious:
                if sus in step.text.lower():
                    risk += 0.4
                    break
        return min(risk, 1.0)
