import time
from gravit.verifier import EpistemicVerifier

def bench_latency(n=1000):
    verifier = EpistemicVerifier()
    times = []
    for _ in range(n):
        start = time.perf_counter()
        verifier.verify(sample_commitment)
        times.append((time.perf_counter() - start) * 1000)  # ms
    print(f"Mean latency: {np.mean(times):.2f} ms")
    print(f"95th percentile: {np.percentile(times, 95):.2f} ms")