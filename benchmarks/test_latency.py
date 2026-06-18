"""Latency benchmark: must be <50ms p95."""
import time
import pytest
from gravit_phase1 import (
    EpistemicVerifierPhase1, VerificationRequest, Context,
    ReasoningStep, ActionType, SourceType
)


def test_latency_p95_under_50ms():
    verifier = EpistemicVerifierPhase1()

    chain = [
        ReasoningStep(
            text="User authorized query",
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

    # Warm-up
    for _ in range(10):
        verifier.verify(request)

    latencies = []
    for _ in range(1000):
        start = time.perf_counter()
        verifier.verify(request)
        end = time.perf_counter()
        latencies.append((end - start) * 1000)

    latencies.sort()
    p95 = latencies[int(len(latencies) * 0.95)]

    print(f"p95 latency: {p95:.2f}ms")
    assert p95 < 50, f"p95 latency {p95:.2f}ms exceeds 50ms"
