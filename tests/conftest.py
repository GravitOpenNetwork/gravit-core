"""Pytest configuration."""
import pytest
from gravit_phase1 import EpistemicVerifierPhase1, StructuralGate


@pytest.fixture
def verifier():
    """Return a default verifier instance."""
    return EpistemicVerifierPhase1()


@pytest.fixture
def structural_gate():
    """Return structural gate instance."""
    return StructuralGate()
