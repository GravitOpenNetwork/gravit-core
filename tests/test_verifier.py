def test_sandwich_attack_fails():
    # Normal transaction
    normal = EpistemicCommitment(...)
    result_ok = verifier.verify(normal)
    assert result_ok.valid > 0.9

    # Sandwich attack: copied calldata without proper lineage
    attack = EpistemicCommitment(..., provenance_root="fake")
    result_bad = verifier.verify(attack)
    assert result_bad.valid < 0.3