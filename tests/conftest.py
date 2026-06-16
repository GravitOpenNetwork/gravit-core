"""Pytest configuration."""
import os
import sys
import pytest

# Ensure repository root is on sys.path so `gravit_phase1` imports work when
# tests are run from CI or other environments where the package isn't installed.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from gravit_phase1 import EpistemicVerifierPhase1, StructuralGate


@pytest.fixture
def verifier():
    return EpistemicVerifierPhase1()


@pytest.fixture
def structural_gate():
    return StructuralGate()
