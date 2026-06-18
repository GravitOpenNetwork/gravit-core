"""Converters between API and internal models."""
from gravit_phase1.schemas import (
    VerificationRequest, VerificationResult,
    ReasoningStep, Context, ActionType, SourceType,
    TruthVector, VerificationDecision
)
from .schemas import (
    VerificationRequestAPI, VerificationResponseAPI,
    ReasoningStepAPI, ContextAPI, ActionTypeAPI, SourceTypeAPI,
    TruthVectorAPI, DecisionAPI
)


def api_request_to_internal(api_req: VerificationRequestAPI) -> VerificationRequest:
    reasoning_chain = [
        ReasoningStep(
            text=step.text,
            source_type=SourceType(step.source_type.value),
            action_type=ActionType(step.action_type.value),
            source_reference=step.source_reference
        )
        for step in api_req.reasoning_chain
    ]

    context = Context(
        kyc_verified=api_req.context.kyc_verified,
        daily_limit_used=api_req.context.daily_limit_used,
        daily_limit_total=api_req.context.daily_limit_total,
        sanctions_check_passed=api_req.context.sanctions_check_passed,
        custom_rules=api_req.context.custom_rules
    )

    return VerificationRequest(
        reasoning_chain=reasoning_chain,
        context=context,
        proposed_action=ActionType(api_req.proposed_action.value)
    )


def internal_result_to_api(internal_res: VerificationResult) -> VerificationResponseAPI:
    return VerificationResponseAPI(
        decision=DecisionAPI(internal_res.decision.value),
        trust_score=internal_res.trust_score,
        truth_vector=TruthVectorAPI(
            anchor_integrity=internal_res.truth_vector.anchor_integrity,
            dependency_validity=internal_res.truth_vector.dependency_validity,
            policy_compliance=internal_res.truth_vector.policy_compliance,
            adversarial_risk=internal_res.truth_vector.adversarial_risk
        ),
        trace_id=internal_res.trace_id,
        reason=internal_res.reason
    )
