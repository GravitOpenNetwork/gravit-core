"""Gravit Phase 1 — Epistemic Verification Layer.

This package implements the structural gate that computes trust scores
and decisions without input from the agent or LLM.
"""

from .schemas import TruthVector, VerificationDecision, Context, ReasoningStep
from .structural_gate import StructuralGate
from .verifier import EpistemicVerifierPhase1
from .audit_proof import AuditProof

__all__ = [
    "TruthVector",
    "VerificationDecision",
    "Context",
    "ReasoningStep",
    "StructuralGate",
    "EpistemicVerifierPhase1",
    "AuditProof",
]
