"""
attack_detector.py — Distributed / coordinated attack detection.

Single responsibility: given the shared store, decide whether a wave of
requests constitutes a coordinated attack and register clusters accordingly.
"""

from datetime import datetime, timedelta
from collections import defaultdict
from typing import Set

from .models import AttackCluster
from .store import RateLimiterStore

# How many distinct IPs + total hits before we call it an attack
MIN_UNIQUE_IPS = 5
MIN_TOTAL_HITS = 20

# How many cluster severity increments before we auto-block
AUTO_BLOCK_SEVERITY = 3
AUTO_BLOCK_DURATION = timedelta(hours=1)

BUFFER_WINDOW = timedelta(minutes=5)


class DistributedAttackDetector:
    """
    Watches the global request buffer and flags coordinated attacks.

    Keeps all detection logic in one place; the RateLimiter just
    calls `scan()` and checks `store.is_coordinated_ip()`.
    """

    def __init__(self, store: RateLimiterStore, logger):
        self._store = store
        self._logger = logger

    def scan(self) -> bool:
        """
        Prune the buffer, group by fingerprint, look for attack patterns.
        Returns True if any attack was detected.
        """
        self._store.prune_global_buffer(BUFFER_WINDOW)

        buffer = self._store.get_global_buffer()
        if len(buffer) < MIN_TOTAL_HITS:
            return False

        # Group IPs by request signature
        sig_to_ips: dict[str, list[str]] = defaultdict(list)
        for _, ip, sig in buffer:
            sig_to_ips[sig].append(ip)

        attack_found = False
        for signature, ips in sig_to_ips.items():
            unique_ips = set(ips)
            if len(unique_ips) >= MIN_UNIQUE_IPS and len(ips) >= MIN_TOTAL_HITS:
                self._register_cluster(unique_ips, signature)
                self._logger.vsilent(
                    f"🚨 DISTRIBUTED ATTACK DETECTED: {len(unique_ips)} IPs, "
                    f"sig: {signature[:8]}...",
                    extra={"ips": list(unique_ips)[:10], "signature": signature},
                )
                attack_found = True

        return attack_found

    # ------------------------------------------------------------------ #

    def _register_cluster(self, ips: Set[str], signature: str):
        store = self._store
        cluster = store.find_cluster_by_signature(signature)

        if cluster:
            cluster.update(ips)
        else:
            cluster = AttackCluster(
                ips=ips.copy(),
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                attack_signature=signature,
                severity=1,
            )
            store.add_attack_cluster(cluster)

        store.add_coordinated_ips(ips)

        if cluster.severity >= AUTO_BLOCK_SEVERITY:
            for ip in ips:
                store.block_ip(ip, AUTO_BLOCK_DURATION)
