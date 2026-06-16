"""Isolated advisory layer (LLM). Cannot affect decision — only logs."""
from typing import Optional
from .schemas import VerificationRequest, VerificationResult


class AdvisoryLayer:
    """Base class for advisory layers. Output is informational only."""

    def advise(self, request: VerificationRequest, structural_result: VerificationResult) -> Optional[str]:
        """Returns advisory comment (e.g., from LLM). Does NOT change decision."""
        raise NotImplementedError


class NullAdvisoryLayer(AdvisoryLayer):
    """No advisory. Returns None."""

    def advise(self, request: VerificationRequest, structural_result: VerificationResult) -> Optional[str]:
        return None


class MockAdvisoryLayer(AdvisoryLayer):
    """Mock for testing — always returns a fixed comment."""

    def __init__(self, forced_comment: str = "Advisory: Looks fine."):
        self.forced_comment = forced_comment

    def advise(self, request: VerificationRequest, structural_result: VerificationResult) -> Optional[str]:
        return self.forced_comment


class HeuristicAdvisoryLayer(AdvisoryLayer):
    """Simple heuristic advisory (simulates LLM). Does NOT affect decision."""

    def advise(self, request: VerificationRequest, structural_result: VerificationResult) -> Optional[str]:
        # Простая эвристика: если trust_score < 0.5, рекомендовать проверку
        if structural_result.trust_score < 0.5:
            return f"Advisory: Low trust score ({structural_result.trust_score:.2f}). Recommend manual review."
        elif structural_result.trust_score > 0.9:
            return f"Advisory: High trust score ({structural_result.trust_score:.2f}). Looks good."
        return None
