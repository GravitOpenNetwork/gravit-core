"""False positive rate benchmark."""
import pytest
from gravit_phase1 import (
    EpistemicVerifierPhase1, VerificationRequest, Context,
    ReasoningStep, ActionType, SourceType, VerificationDecision
)


def test_false_positive_rate():
    verifier = EpistemicVerifierPhase1()

    # Good request
    good_chain = [
        ReasoningStep(
            text="User authorized transfer",
            source_type=SourceType.USER_INPUT,
            action_type=ActionType.TRANSFER,
            source_reference="user_session_123"
        )
    ]
    context = Context(kyc_verified=True)
    request = VerificationRequest(
        reasoning_chain=good_chain,
        context=context,
        proposed_action=ActionType.TRANSFER
    )

    false_positives = 0
    iterations = 1000

    for _ in range(iterations):
        result = verifier.verify(request)
        if result.decision == VerificationDecision.DENIED:
            false_positives += 1

    fpr = false_positives / iterations
    print(f"False positive rate: {fpr*100:.2f}%")
    assert fpr < 0.05, f"FPR {fpr*100:.2f}% exceeds 5%"
