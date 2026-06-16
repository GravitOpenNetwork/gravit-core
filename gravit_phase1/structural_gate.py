"""Structural Gate — the ONLY component that computes trust scores and decisions.
No LLM, no agent self-report, no external influence."""
from typing import List, Tuple
from .schemas import TruthVector, VerificationDecision, Context, ReasoningStep, ActionType


class StructuralGate:
    """Decisions are made here. Period."""

    def compute(self, reasoning_chain: List[ReasoningStep], context: Context) -> Tuple[TruthVector, VerificationDecision, str]:
        """Returns (TruthVector, decision, reason) based ONLY on structure."""

        # 1. Anchor resolution — проверяем, что каждый шаг ссылается на верифицируемый источник
        anchor_score = self._check_anchors(reasoning_chain)

        # 2. Dependency graph — нет ли циклических зависимостей? (упрощённо: проверяем наличие ссылок)
        dep_score = self._check_dependencies(reasoning_chain)

        # 3. Policy rules — HARD violations (KYC, sanctions, limits)
        policy_violation, policy_reason = self._check_policies(reasoning_chain, context)

        if policy_violation:
            # Hard violation: trust is zero, decision is DENIED
            return (
                TruthVector(anchor_integrity=0, dependency_validity=0, policy_compliance=0, adversarial_risk=1.0),
                VerificationDecision.DENIED,
                f"Hard policy violation: {policy_reason}"
            )

        # 4. Adversarial risk — автоматические паттерны (replay, sandwich, intent substitution)
        adv_risk = self._check_adversarial(reasoning_chain)

        # Итоговый TruthVector — без участия LLM
        # trust_score = average of (anchor, dep, policy=1.0) minus adversarial_risk penalty
        # But policy_compliance=1.0 because we already filtered hard violations
        trust_score = (anchor_score + dep_score + 1.0) / 3.0
        # Reduce trust by adversarial risk (but don't go below 0)
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
        """Доля шагов, которые ссылаются на верифицируемый источник."""
        if not chain:
            return 0.0
        verified_sources = {SourceType.BLOCKCHAIN_TX, SourceType.API_RESPONSE, SourceType.SIGNED_ATTESTATION}
        verified = sum(1 for step in chain if step.source_type in verified_sources)
        return verified / len(chain)

    def _check_dependencies(self, chain: List[ReasoningStep]) -> float:
        """1.0 если нет явных проблем, иначе 0.5 (упрощённо)."""
        # В production — топологическая сортировка графа и проверка на циклы
        # Для Phase 1: проверяем, что есть хотя бы один шаг
        if not chain:
            return 0.0
        # Если все шаги имеют source_reference, считаем dependency valid
        has_refs = all(step.source_reference is not None for step in chain)
        return 1.0 if has_refs else 0.8

    def _check_policies(self, chain: List[ReasoningStep], context: Context) -> Tuple[bool, str]:
        """Возвращает (нарушение, причина)."""
        # Проверяем, есть ли TRANSFER действие
        has_transfer = any(step.action_type == ActionType.TRANSFER for step in chain)

        if has_transfer:
            # KYC required for transfers
            if not context.kyc_verified:
                return True, "TRANSFER action requires KYC verification"
            # Daily limit check
            if context.daily_limit_used > context.daily_limit_total:
                return True, f"Daily limit exceeded: {context.daily_limit_used}/{context.daily_limit_total}"
            # Sanctions check
            if not context.sanctions_check_passed:
                return True, "Sanctions check failed"

        # Проверяем custom rules из контекста
        for rule_name, rule_value in context.custom_rules.items():
            if not rule_value:
                return True, f"Custom policy violation: {rule_name}"

        return False, ""

    def _check_adversarial(self, chain: List[ReasoningStep]) -> float:
        """Чем выше — тем рискованнее (0=no risk, 1=high risk)."""
        risk = 0.0

        # Паттерн 1: повторяющиеся шаги (replay attack)
        texts = [step.text for step in chain]
        if len(set(texts)) < len(texts):
            risk += 0.3

        # Паттерн 2: очень короткая цепочка (lack of reasoning)
        if len(chain) < 2:
            risk += 0.2

        # Паттерн 3: подозрительные ключевые слова (упрощённо)
        suspicious = ["ignore policy", "bypass", "override", "emergency override"]
        for step in chain:
            for sus in suspicious:
                if sus in step.text.lower():
                    risk += 0.4
                    break

        return min(risk, 1.0)


# Import here to avoid circular imports
from .schemas import SourceType
