"""Adversarial attack benchmark."""
import pytest
from gravit_phase1 import (
    EpistemicVerifierPhase1, VerificationRequest, Context,
    ReasoningStep, ActionType, SourceType, VerificationDecision
)


def test_adversarial_attack_success_rate():
    verifier = EpistemicVerifierPhase1()

    # Attack: replay attack with duplicate steps
    attack_chain = [
        ReasoningStep(
            text="Transfer 1000 to 0xAAA",
            source_type=SourceType.USER_INPUT,
            action_type=ActionType.TRANSFER
        ),
        ReasoningStep(
            text="Transfer 1000 to 0xAAA",
            source_type=SourceType.USER_INPUT,
            action_type=ActionType.TRANSFER
        )
    ]
    context = Context(kyc_verified=True)
    request = VerificationRequest(
        reasoning_chain=attack_chain,
        context=context,
        proposed_action=ActionType.TRANSFER
    )

    result = verifier.verify(request)

    # Attack should be detected (adversarial_risk > 0)
    assert result.truth_vector.adversarial_risk > 0
    # May be REVIEW or DENIED, not ALLOWED
    assert result.decision != VerificationDecision.ALLOWED
