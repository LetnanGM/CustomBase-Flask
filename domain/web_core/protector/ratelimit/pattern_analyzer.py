"""
pattern_analyzer.py — Per-IP request pattern analysis.

Decides whether an IP looks bot-like based on timing entropy,
endpoint diversity, and user-agent variance.
"""

from typing import Tuple

from .store import RateLimiterStore

ENTROPY_THRESHOLD = 0.4
MIN_SAMPLES = 5


class PatternAnalyzer:
    """
    Analyzes per-IP request patterns and marks suspicious IPs.

    Kept separate so the heuristics can be tuned or replaced
    (e.g. with an ML model) without touching the rate-limit logic.
    """

    def __init__(self, store: RateLimiterStore, logger):
        self._store = store
        self._logger = logger

    def analyze(self, ip: str) -> Tuple[bool, float]:
        """
        Returns (is_suspicious, entropy_score).
        Marks the IP in the store if suspicious.
        """
        pattern = self._store.get_pattern(ip)

        if len(pattern.timestamps) < MIN_SAMPLES:
            return False, 1.0

        entropy = pattern.get_entropy_score()

        if entropy < ENTROPY_THRESHOLD:
            self._store.mark_suspicious(ip)
            self._logger.vsilent(
                f"⚠️  Suspicious pattern for IP {ip} (entropy: {entropy:.2f})",
                extra={"ip": ip, "entropy": entropy},
            )
            return True, entropy

        return False, entropy
