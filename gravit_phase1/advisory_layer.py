"""Isolated advisory layer (LLM). Cannot affect decision."""
from typing import Optional
from .schemas import VerificationRequest, VerificationResult


class AdvisoryLayer:
    def advise(self, request: VerificationRequest, result: VerificationResult) -> Optional[str]:
        raise NotImplementedError


class NullAdvisoryLayer(AdvisoryLayer):
    def advise(self, request: VerificationRequest, result: VerificationResult) -> Optional[str]:
        return None


class MockAdvisoryLayer(AdvisoryLayer):
    def __init__(self, forced_comment: str = "Advisory: Looks fine."):
        self.forced_comment = forced_comment

    def advise(self, request: VerificationRequest, result: VerificationResult) -> Optional[str]:
        return self.forced_comment


class HeuristicAdvisoryLayer(AdvisoryLayer):
    def advise(self, request: VerificationRequest, result: VerificationResult) -> Optional[str]:
        if result.trust_score < 0.5:
            return f"Advisory: Low trust score ({result.trust_score:.2f}). Review required."
        elif result.trust_score > 0.9:
            return f"Advisory: High trust score ({result.trust_score:.2f})."
        return None
