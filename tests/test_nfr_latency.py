import time

import pytest
import requests

BASE_URL = "http://127.0.0.1:8000/media/"
USER_ID = "123"


@pytest.mark.nfr
def test_p95_latency():
    latencies = []

    for _ in range(50):
        start = time.time()
        response = requests.get(BASE_URL, headers={"X-User-Id": USER_ID})
        elapsed = time.time() - start
        latencies.append(elapsed)
        assert response.status_code == 200, f"Unexpected status: {response.status_code}"

    latencies.sort()
    index_95 = int(0.95 * len(latencies)) - 1
    p95 = latencies[index_95]

    print(f"\n[p95 latency] {p95:.3f} s")

    threshold = 0.2
    assert p95 <= threshold, f"p95 latency {p95:.3f}s > {threshold}s"
