"""
store.py — In-memory storage layer for the rate limiter.

All mutable state lives here. If you want to swap to Redis, Memcached,
or a DB later, just replace this class — nothing else changes.
"""

from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional

from .models import RequestPattern, AttackCluster


class RateLimiterStore:
    """
    Central in-memory store for all rate-limiter state.

    Designed so the storage backend can be swapped without touching
    any business logic.  A Redis-backed version, for example, would
    implement the same public interface.
    """

    def __init__(self):
        # --- per-IP request history ---
        self._requests: Dict[str, List[datetime]] = defaultdict(list)
        self._login_attempts: Dict[str, List[datetime]] = defaultdict(list)

        # --- block lists ---
        self._blocked_ips: Dict[str, datetime] = {}  # ip -> unblock_at
        self._fingerprint_blocks: Dict[str, datetime] = {}  # fingerprint -> unblock_at

        # --- pattern / anomaly tracking ---
        self._request_patterns: Dict[str, RequestPattern] = defaultdict(RequestPattern)
        self._suspicious_ips: Set[str] = set()

        # --- distributed-attack tracking ---
        self._attack_clusters: List[AttackCluster] = []
        self._coordinated_ips: Set[str] = set()

        # (timestamp, ip, fingerprint)
        self._global_request_buffer: List[Tuple[datetime, str, str]] = []

    # ------------------------------------------------------------------ #
    # Block lists
    # ------------------------------------------------------------------ #

    def is_ip_blocked(self, ip: str) -> bool:
        return self._check_expiry(self._blocked_ips, ip)

    def block_ip(self, ip: str, duration: timedelta):
        self._blocked_ips[ip] = datetime.now() + duration

    def is_fingerprint_blocked(self, fingerprint: str) -> bool:
        return self._check_expiry(self._fingerprint_blocks, fingerprint)

    def block_fingerprint(self, fingerprint: str, duration: timedelta):
        self._fingerprint_blocks[fingerprint] = datetime.now() + duration

    def _check_expiry(self, store: dict, key: str) -> bool:
        """Return True if key is in store and still within block window."""
        expiry = store.get(key)
        if expiry is None:
            return False
        if datetime.now() < expiry:
            return True
        del store[key]
        return False

    # ------------------------------------------------------------------ #
    # Request history
    # ------------------------------------------------------------------ #

    def get_requests(self, ip: str) -> List[datetime]:
        return self._requests[ip]

    def add_request(self, ip: str, timestamp: datetime):
        self._requests[ip].append(timestamp)

    def prune_requests(self, ip: str, window: timedelta):
        cutoff = datetime.now() - window
        self._requests[ip] = [t for t in self._requests[ip] if t >= cutoff]

    def get_recent_requests(self, ip: str, window: timedelta) -> List[datetime]:
        cutoff = datetime.now() - window
        return [t for t in self._requests[ip] if t >= cutoff]

    # ------------------------------------------------------------------ #
    # Login attempts
    # ------------------------------------------------------------------ #

    def get_login_attempts(self, ip: str) -> List[datetime]:
        return self._login_attempts[ip]

    def add_login_attempt(self, ip: str):
        self._login_attempts[ip].append(datetime.now())

    def prune_login_attempts(self, ip: str, window: timedelta):
        cutoff = datetime.now() - window
        self._login_attempts[ip] = [t for t in self._login_attempts[ip] if t >= cutoff]

    def count_ips_with_login_attempts(self, exclude_ip: str) -> int:
        return sum(
            1
            for ip, attempts in self._login_attempts.items()
            if ip != exclude_ip and attempts
        )

    # ------------------------------------------------------------------ #
    # Pattern tracking
    # ------------------------------------------------------------------ #

    def get_pattern(self, ip: str) -> RequestPattern:
        return self._request_patterns[ip]

    def mark_suspicious(self, ip: str):
        self._suspicious_ips.add(ip)

    def is_suspicious(self, ip: str) -> bool:
        return ip in self._suspicious_ips

    # ------------------------------------------------------------------ #
    # Distributed attack tracking
    # ------------------------------------------------------------------ #

    def add_to_global_buffer(self, timestamp: datetime, ip: str, fingerprint: str):
        self._global_request_buffer.append((timestamp, ip, fingerprint))

    def get_global_buffer(self) -> List[Tuple[datetime, str, str]]:
        return self._global_request_buffer

    def prune_global_buffer(self, window: timedelta):
        cutoff = datetime.now() - window
        self._global_request_buffer = [
            (ts, ip, sig) for ts, ip, sig in self._global_request_buffer if ts >= cutoff
        ]

    def get_attack_clusters(self) -> List[AttackCluster]:
        return self._attack_clusters

    def add_attack_cluster(self, cluster: AttackCluster):
        self._attack_clusters.append(cluster)

    def find_cluster_by_signature(self, signature: str) -> Optional[AttackCluster]:
        for cluster in self._attack_clusters:
            if cluster.attack_signature == signature:
                return cluster
        return None

    def add_coordinated_ip(self, ip: str):
        self._coordinated_ips.add(ip)

    def add_coordinated_ips(self, ips: Set[str]):
        self._coordinated_ips.update(ips)

    def is_coordinated_ip(self, ip: str) -> bool:
        return ip in self._coordinated_ips

    def discard_coordinated_ip(self, ip: str):
        self._coordinated_ips.discard(ip)

    # ------------------------------------------------------------------ #
    # Cleanup
    # ------------------------------------------------------------------ #

    def cleanup(self, cluster_ttl: timedelta, pattern_idle_ttl: timedelta):
        now = datetime.now()

        self._attack_clusters = [
            c for c in self._attack_clusters if now - c.last_seen < cluster_ttl
        ]

        for ip in list(self._request_patterns):
            pattern = self._request_patterns[ip]
            if pattern.timestamps and now - pattern.timestamps[-1] > pattern_idle_ttl:
                del self._request_patterns[ip]

        self._suspicious_ips = {
            ip for ip in self._suspicious_ips if ip in self._request_patterns
        }

    # ------------------------------------------------------------------ #
    # Stats
    # ------------------------------------------------------------------ #

    def stats(self) -> dict:
        return {
            "blocked_ips": len(self._blocked_ips),
            "suspicious_ips": len(self._suspicious_ips),
            "coordinated_ips": len(self._coordinated_ips),
            "fingerprint_blocks": len(self._fingerprint_blocks),
            "attack_clusters": len(self._attack_clusters),
            "total_requests_tracked": sum(len(v) for v in self._requests.values()),
        }
