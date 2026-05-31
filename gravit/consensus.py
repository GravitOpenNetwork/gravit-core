import numpy as np
from scipy.special import softmax

def cross_entropy(p: np.ndarray, q: np.ndarray) -> float:
    """Compute cross-entropy between two probability distributions."""
    return -np.sum(p * np.log(q + 1e-12))

def grtvp_consensus(hypotheses: list, stakes: list, reputations: list) -> dict:
    """
    Input: list of (hypothesis_distribution, stake, reputation)
    Output: final truth vector
    """
    n = len(hypotheses)
    weights = [0.4 * stake + 0.6 * rep for stake, rep in zip(stakes, reputations)]

    # Detect outliers via cross-entropy
    scores = []
    for i in range(n):
        ce_sum = 0
        for j in range(n):
            if i != j:
                ce_sum += cross_entropy(hypotheses[i], hypotheses[j])
        scores.append(ce_sum / (n-1))

    # Outlier threshold
    threshold = np.mean(scores) + 2 * np.std(scores)
    outlier_indices = [i for i, s in enumerate(scores) if s > threshold]

    # Reduce weight for outliers
    for i in outlier_indices:
        weights[i] *= 0.5

    # Final weighted average
    weighted_h = np.average(hypotheses, axis=0, weights=weights)
    return {"truth_vector": softmax(weighted_h).tolist(), "outliers": outlier_indices}