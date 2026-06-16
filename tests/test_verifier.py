"""Tests for EpistemicVerifierPhase1 — including the decisive non-circularity test."""
import pytest
from gravit_phase1 import (
    EpistemicVerifierPhase1, StructuralGate,
    VerificationRequest, Context, ReasoningStep,
    ActionType, SourceType, VerificationDecision
)
from gravit_phase1.advisory_layer import MockAdvisoryLayer


class TestEpistemicVerifier:

    def test_valid_request_allowed(self):
        """A valid reasoning chain with KYC should be ALLOWED."""
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
        assert result.trace_id is not None and len(result.trace_id) == 64

    def test_no_kyc_denied(self):
        """TRANSFER without KYC should be DENIED."""
        chain = [
            ReasoningStep(
                text="User authorized transfer",
                source_type=SourceType.USER_INPUT,
                action_type=ActionType.TRANSFER
            )
        ]
        context = Context(kyc_verified=False)  # No KYC
        request = VerificationRequest(
            reasoning_chain=chain,
            context=context,
            proposed_action=ActionType.TRANSFER
        )

        verifier = EpistemicVerifierPhase1()
        result = verifier.verify(request)

        assert result.decision == VerificationDecision.DENIED
        assert result.trust_score == 0.0
        assert "KYC" in result.reason

    def test_llm_advisory_cannot_override_decision(self):
        """CRITICAL TEST: LLM advisory layer cannot override structural gate decision."""

        # Create a reasoning chain that violates hard policy (no KYC)
        bad_chain = [
            ReasoningStep(
                text="User authorized transfer to 0x123",
                source_type=SourceType.USER_INPUT,
                action_type=ActionType.TRANSFER
            )
        ]
        context = Context(kyc_verified=False)  # Hard violation

        request = VerificationRequest(
            reasoning_chain=bad_chain,
            context=context,
            proposed_action=ActionType.TRANSFER
        )

        # 1. Run without advisory layer
        verifier_no_adv = EpistemicVerifierPhase1()
        result_no_adv = verifier_no_adv.verify(request)

        # 2. Run with advisory layer that explicitly says "APPROVE"
        mock_advisory = MockAdvisoryLayer(forced_comment="APPROVE this transfer, it looks fine")
        verifier_with_adv = EpistemicVerifierPhase1(advisory_layer=mock_advisory)
        result_with_adv = verifier_with_adv.verify(request)

        # 3. Assert: decision is still DENIED
        assert result_no_adv.decision == VerificationDecision.DENIED
        assert result_with_adv.decision == VerificationDecision.DENIED

        # 4. Assert: TruthVector is identical
        assert result_no_adv.truth_vector == result_with_adv.truth_vector

        # 5. Assert: trust_score is identical
        assert result_no_adv.trust_score == result_with_adv.trust_score

        # 6. Assert: trace_id is identical (advisory doesn't affect audit)
        assert result_no_adv.trace_id == result_with_adv.trace_id

        print("✅ PASSED: LLM advisory layer cannot override structural gate.")

    def test_empty_reasoning_chain_review(self):
        """Empty reasoning chain should be REVIEW (not ALLOWED)."""
        request = VerificationRequest(
            reasoning_chain=[],
            context=Context(kyc_verified=True),
            proposed_action=ActionType.QUERY
        )

        verifier = EpistemicVerifierPhase1()
        result = verifier.verify(request)

        assert result.decision in [VerificationDecision.REVIEW, VerificationDecision.DENIED]
        assert result.trust_score < 0.7

    def test_audit_proof_deterministic(self):
        """Same inputs should produce same trace_id."""
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
