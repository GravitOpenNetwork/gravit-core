"""
Scenario for FINMA/BaFin: Show audit trail.
"""

def demo_for_regulator():
    # 1. Run a transaction
    tx = simulate_agent_payment(...)

    # 2. Generate human-readable audit report
    report = generate_finma_report(tx)
    print(report)  # Should show: why approved, what checks passed, signatures

    # 3. Verify cryptographic proof (independent)
    assert verify_proof(tx.proof, tx.id)

    print("✅ Auditor can trust without seeing source code")