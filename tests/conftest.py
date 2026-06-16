"""Pytest configuration."""
import pytest
from gravit_phase1 import EpistemicVerifierPhase1, StructuralGate


@pytest.fixture
def verifier():
    return EpistemicVerifierPhase1()


@pytest.fixture
def structural_gate():
    return StructuralGate()
