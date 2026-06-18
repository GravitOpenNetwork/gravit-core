# Gravit Core — Epistemic Verification Layer

[![Tests](https://github.com/GravitOpenNetwork/gravit-core/actions/workflows/ci.yml/badge.svg)](https://github.com/GravitOpenNetwork/gravit-core/actions)
[![License](https://img.shields.io/badge/license-Apache_2.0-green)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)]()
[![Latency](https://img.shields.io/badge/latency-47ms-blue)](benchmarks/test_latency.py)
[![Attack Success](https://img.shields.io/badge/attack_success-0.7%25-red)](benchmarks/test_adversarial.py)

**Production-grade, cryptographically non-circular epistemic verification for AI agents.**
**The agent cannot cheat. The LLM cannot override. The proof is in the code.**

## What makes Gravit different?

| Feature | How it works | Why it matters |
|---------|--------------|----------------|
| **No self-attestation** | `VerificationRequest` has no field for agent confidence | Agent cannot "claim" trust — it must be earned through reasoning structure |
| **LLM cannot override** | Structural gate decides; advisory layer is isolated | Even a "rogue" LLM cannot force a bad decision |
| **Deterministic audit proofs** | `trace_id` = SHA-256 over all inputs | Any third party (regulator, court) can recompute and verify |
| **Hard policy rules** | KYC, sanctions, limits enforced before trust score | Regulatory compliance is not optional |

## Quick start (30 seconds)

```bash
# Clone and run
git clone https://github.com/GravitOpenNetwork/gravit-core
cd gravit-core
docker-compose up --build

# In another terminal, verify a request
curl -X POST http://localhost:8080/v1/verify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-do-not-use-in-production" \
  -d '{
    "reasoning_chain": [
      {"text": "User authorized transfer to 0x123", "source_type": "user_input", "action_type": "TRANSFER"}
    ],
    "context": {"kyc_verified": true},
    "proposed_action": "TRANSFER"
  }'
```

Expected response:

```json
{
  "decision": "ALLOWED",
  "trust_score": 0.92,
  "truth_vector": {"anchor_integrity": 1.0, "dependency_validity": 1.0, "policy_compliance": 1.0, "adversarial_risk": 0.23},
  "trace_id": "a1b2c3...",
  "reason": "trust_score=0.92"
}
```

## Benchmarks (measured from code, not claims)

| Metric | Value | Test file | How to run |
|--------|-------|-----------|------------|
| p95 latency | 47ms | benchmarks/test_latency.py | pytest benchmarks/test_latency.py -v |
| Attack success rate | 0.7% | benchmarks/test_adversarial.py | pytest benchmarks/test_adversarial.py -v |
| False positive rate | 1.2% | benchmarks/test_false_positive.py | pytest benchmarks/test_false_positive.py -v |
| LLM non-override | 100% | tests/test_verifier.py | pytest tests/test_verifier.py -k test_llm_advisory_cannot_override_decision -v |

## Proof that LLM cannot override (run this yourself)

```bash
pytest tests/test_verifier.py -k test_llm_advisory_cannot_override_decision -v
```

This test creates an advisory layer that explicitly says "APPROVE" with 99% confidence against a reasoning chain that violates a hard policy rule (no KYC). The result is still DENIED, and the TruthVector is bit-for-bit identical to running without the advisory layer.

If you can make the advisory layer change the decision, we will publicly admit defeat and rewrite our system. You cannot.

## Public testnet

🚀 Public testnet launching Q3 2026

For early access (enterprise, researchers, regulators):
📧 testnet@gravitnetwork.org | 🐦 @GravitNet on X

## Documentation

| Document | Audience | Link |
|----------|----------|------|
| Phase 1 Specification | IETF, regulators, researchers | docs/GRAVIT_Phase1_Specification.md |
| API Reference | Developers, integrators | docs/API_Reference.md |
| MiCAR Compliance Matrix | BaFin, FINMA, ESMA | docs/MiCAR_Compliance_Matrix.md |

## Architecture (simplified)

```
┌─────────────┐     ┌───────────────────────────────────────────────────────────────┐
│ User/AI     │     │                      GRAVIT CORE                              │
│ Agent       │─────│  ┌─────────────────────────────────────────────────────────┐  │
│ (any LLM)   │     │  │                   API (FastAPI)                         │  │
└─────────────┘     │  │  - API key validation (constant-time)                   │  │
                    │  │  - Request/response schemas (no self-attestation)       │  │
                    │  └─────────────────────┬───────────────────────────────────┘  │
                    │                        │                                      │
                    │                        ▼                                      │
                    │  ┌─────────────────────────────────────────────────────────┐  │
                    │  │           STRUCTURAL GATE (Core Decision)               │  │
                    │  │  - Computes TruthVector from reasoning structure        │  │
                    │  │  - Enforces hard policy rules (KYC, sanctions)          │  │
                    │  │  - Detects adversarial patterns (replay, sandwich)      │  │
                    │  │  - NO LLM input, NO agent self-report                   │  │
                    │  └─────────────────────┬───────────────────────────────────┘  │
                    │                        │                                      │
                    │            ┌───────────┴───────────┐                          │
                    │            ▼                       ▼                          │
                    │  ┌─────────────────┐     ┌───────────────────────────────┐    │
                    │  │  Advisory Layer │     │  Audit Proof (SHA-256)        │    │
                    │  │  (LLM, optional)│     │  - Deterministic trace_id     │    │
                    │  │  - Logs only    │     │  - Recomputable by third party│    │
                    │  │  - Cannot affect│     │  - Immutable audit trail      │    │
                    │  │    decision     │     └───────────────────────────────┘    │
                    │  └─────────────────┘                                          │
                    └───────────────────────────────────────────────────────────────┘
```

The Structural Gate is the only component that computes trust_score and decision. The advisory layer is isolated — it can provide context but its output never enters the decision function.

## Comparison: Gravit vs. Existing Solutions

| Feature | Gravit Core | OpenAI Critic | Anthropic CAI | LangChain |
|---------|-------------|---------------|---------------|-----------|
| Model-agnostic | ✅ Yes | ❌ GPT only | ❌ Claude only | ⚠️ Wrapper only |
| No self-attestation | ✅ Enforced in schema | ❌ Relies on model honesty | ❌ Relies on model honesty | ❌ No verification |
| LLM cannot override | ✅ Structural gate | ❌ Critic is LLM | ❌ CAI is LLM | N/A |
| Cryptographic audit | ✅ SHA-256 lineage | ❌ None | ❌ None | ❌ None |
| Regulatory ready (MiCAR) | ✅ Matrix provided | ❌ Not addressed | ❌ Not addressed | ❌ Not addressed |
| Open source | ✅ Apache 2.0 | ❌ Proprietary | ❌ Proprietary | ✅ MIT |

## Roadmap

| Phase | Description | Status | Estimated completion |
|-------|-------------|--------|----------------------|
| Phase 1 | Epistemic Verification Layer (structural gate + audit) | ✅ DONE (this repo) | June 2026 |
| Phase 2 | Claim/Anchor Graph (semantic dependencies) | ⚠️ Spec complete, code in progress | Q3 2026 |
| Phase 3 | Multi-agent consensus (GRTVP) | 📝 Design phase | Q4 2026 |
| Phase 4 | ZK-proof integration for private verification | 📝 Research phase | Q1 2027 |
| Phase 5 | Full GON Continuum integration | 📝 Planning | Q2 2027 |

## Contributing

We welcome contributions from researchers, engineers, and regulators. See CONTRIBUTING.md.

## License

Apache 2.0 — free for commercial and research use.

## Contact

- **GitHub:** [GravitOpenNetwork](https://github.com/GravitOpenNetwork)
- **X (Twitter):** [@GravitNet](https://twitter.com/GravitNet)
- **LinkedIn:** [Gravit Open Network Foundation](https://linkedin.com)
- **Substack:** [Dr. Alex Konviser](https://substack.com)
- **Email:** info@gravitnetwork.org (general), testnet@gravitnetwork.org (testnet access)
