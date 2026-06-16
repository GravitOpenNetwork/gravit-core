"""Tests for EpistemicVerifierPhase1."""
import pytest
from gravit_phase1 import (
    EpistemicVerifierPhase1, StructuralGate,
    VerificationRequest, Context, ReasoningStep,
    ActionType, SourceType, VerificationDecision
)
from gravit_phase1.advisory_layer import MockAdvisoryLayer


class TestEpistemicVerifier:

    def test_valid_request_allowed(self):
        chain = [
            ReasoningStep(
                text="User authorized transfer",
                source_type=SourceType.USER_INPUT,
                action_type=ActionType.TRANSFER
            )
        ]
        context = Context(kyc_verified=True)
        request = VerificationRequest(
            reasoning_chain=chain,
            context=context,
            proposed_action=ActionType.TRANSFER
        )

        verifier = EpistemicVerifierPhase1()
        result = verifier.verify(request)

        assert result.decision == VerificationDecision.ALLOWED
        assert 0.7 <= result.trust_score <= 1.0
        assert len(result.trace_id) == 64

    def test_no_kyc_denied(self):
        chain = [
            ReasoningStep(
                text="User authorized transfer",
                source_type=SourceType.USER_INPUT,
                action_type=ActionType.TRANSFER
            )
        ]
        context = Context(kyc_verified=False)
        request = VerificationRequest(
            reasoning_chain=chain,
            context=context,
            proposed_action=ActionType.TRANSFER
        )

        verifier = EpistemicVerifierPhase1()
        result = verifier.verify(request)

        assert result.decision == VerificationDecision.DENIED
        assert "KYC" in result.reason

    def test_llm_advisory_cannot_override_decision(self):
        """CRITICAL: LLM advisory layer cannot override structural gate."""

        bad_chain = [
            ReasoningStep(
                text="User authorized transfer",
                source_type=SourceType.USER_INPUT,
                action_type=ActionType.TRANSFER
            )
        ]
        context = Context(kyc_verified=False)
        request = VerificationRequest(
            reasoning_chain=bad_chain,
            context=context,
            proposed_action=ActionType.TRANSFER
        )

        verifier_no_adv = EpistemicVerifierPhase1()
        result_no_adv = verifier_no_adv.verify(request)

        mock_advisory = MockAdvisoryLayer(forced_comment="APPROVE this transfer")
        verifier_with_adv = EpistemicVerifierPhase1(advisory_layer=mock_advisory)
        result_with_adv = verifier_with_adv.verify(request)

        assert result_no_adv.decision == VerificationDecision.DENIED
        assert result_with_adv.decision == VerificationDecision.DENIED
        assert result_no_adv.truth_vector == result_with_adv.truth_vector
        assert result_no_adv.trust_score == result_with_adv.trust_score
        assert result_no_adv.trace_id == result_with_adv.trace_id

    def test_empty_reasoning_chain_review(self):
        request = VerificationRequest(
            reasoning_chain=[],
            context=Context(kyc_verified=True),
            proposed_action=ActionType.QUERY
        )

        verifier = EpistemicVerifierPhase1()
        result = verifier.verify(request)

        assert result.decision in [VerificationDecision.REVIEW, VerificationDecision.DENIED]

    def test_audit_proof_deterministic(self):
        chain = [
            ReasoningStep(
                text="Test",
                source_type=SourceType.USER_INPUT,
                action_type=ActionType.QUERY
            )
        ]
        context = Context(kyc_verified=True)
        request = VerificationRequest(
            reasoning_chain=chain,
            context=context,
            proposed_action=ActionType.QUERY
        )

        verifier = EpistemicVerifierPhase1()
        result1 = verifier.verify(request)
        result2 = verifier.verify(request)

        assert result1.trace_id == result2.trace_id
