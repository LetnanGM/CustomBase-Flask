"""
rate_limiter.py — Thin orchestrator.

Each concern lives in its own class.  This file wires them together
and exposes the public API that the rest of the app uses.
"""

from datetime import datetime, timedelta
from typing import Dict

from ...data.configuration.sys.SecurityConfig import SecurityConfig
from ...bootstrap import rl_logger

from .store import RateLimiterStore
from .attack_detector import DistributedAttackDetector
from .pattern_analyzer import PatternAnalyzer
from . import fingerprint as fp

# Block durations
FINGERPRINT_BLOCK_DURATION = timedelta(minutes=30)
LOGIN_LOCKOUT_HOURS = 2


class RateLimiter:
    """
    Advanced rate limiter with distributed attack detection.

    Orchestrates:
      - RateLimiterStore       (all mutable state)
      - DistributedAttackDetector  (coordinated-attack logic)
      - PatternAnalyzer        (per-IP anomaly detection)
    """

    def __init__(self):
        self._store = RateLimiterStore()
        self._attack_detector = DistributedAttackDetector(self._store, rl_logger)
        self._pattern_analyzer = PatternAnalyzer(self._store, rl_logger)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def is_blocked(self, ip: str) -> bool:
        """True if the IP is hard-blocked or part of an active attack cluster."""
        if self._store.is_ip_blocked(ip):
            return True

        return self._is_in_active_cluster(ip)

    def check_rate_limit(
        self,
        ip: str,
        user_agent: str = "",
        endpoint: str = "",
        method: str = "GET",
    ) -> bool:
        """
        Main gate — returns True if the request is allowed.

        Steps:
          1. Whitelist check
          2. Fingerprint block check
          3. Distributed-attack scan
          4. Record + analyze request pattern
          5. Apply (adaptive) per-minute / per-hour limits
        """
        if ip in SecurityConfig.WHITELISTED_IPS:
            return True

        fingerprint = fp.generate(ip, user_agent, endpoint, method)

        if self._store.is_fingerprint_blocked(fingerprint):
            rl_logger.vsilent(
                f"🔒 Blocked by fingerprint {fingerprint[:8]}… IP: {ip}",
                extra={"ip": ip, "fingerprint": fingerprint},
            )
            return False

        self._store.add_to_global_buffer(datetime.now(), ip, fingerprint)

        if self._attack_detector.scan() and self._store.is_coordinated_ip(ip):
            return False

        self._record_request(ip, endpoint, user_agent, fingerprint)

        is_suspicious, _ = self._pattern_analyzer.analyze(ip)

        return self._within_limits(ip, fingerprint, is_suspicious)

    def check_login_attempts(self, ip: str, username: str = "") -> bool:
        """True if the IP has not exceeded the login-attempt threshold."""
        lockout = timedelta(seconds=SecurityConfig.LOGIN_LOCKOUT_DURATION)
        self._store.prune_login_attempts(ip, lockout)

        if username and self._distributed_brute_force_detected(ip, username):
            if (
                len(self._store.get_login_attempts(ip))
                >= SecurityConfig.MAX_LOGIN_ATTEMPTS // 2
            ):
                self._store.block_ip(ip, timedelta(hours=LOGIN_LOCKOUT_HOURS))
                return False

        if len(self._store.get_login_attempts(ip)) >= SecurityConfig.MAX_LOGIN_ATTEMPTS:
            self._store.block_ip(ip, lockout)
            rl_logger.vsilent(
                f"🔒 Too many login attempts — IP blocked: {ip}", extra={"ip": ip}
            )
            return False

        return True

    def record_login_attempt(self, ip: str):
        """Record a failed login attempt."""
        self._store.add_login_attempt(ip)

    def get_attack_statistics(self) -> Dict:
        """Return current attack/rate-limit counters."""
        base = self._store.stats()
        active = sum(
            1
            for c in self._store.get_attack_clusters()
            if datetime.now() - c.last_seen < timedelta(minutes=30)
        )
        base["active_clusters"] = active
        return base

    def cleanup_old_data(self):
        """Periodic housekeeping — call from a scheduled task."""
        self._store.cleanup(
            cluster_ttl=timedelta(hours=24),
            pattern_idle_ttl=timedelta(hours=2),
        )
        rl_logger.vsilent("🧹 Cleaned up old rate limiter data")

    # ------------------------------------------------------------------ #
    # Private helpers
    # ------------------------------------------------------------------ #

    def _record_request(
        self, ip: str, endpoint: str, user_agent: str, fingerprint: str
    ):
        now = datetime.now()
        self._store.prune_requests(ip, timedelta(hours=1))
        self._store.get_pattern(ip).record(now, endpoint, user_agent, fingerprint)

    def _within_limits(self, ip: str, fingerprint: str, is_suspicious: bool) -> bool:
        """Apply per-minute and per-hour caps, with tighter limits for suspicious IPs."""
        max_per_minute = SecurityConfig.MAX_REQUESTS_PER_MINUTE
        max_per_hour = SecurityConfig.MAX_REQUESTS_PER_HOUR

        if is_suspicious:
            max_per_minute //= 2
            max_per_hour //= 2

        recent_minute = self._store.get_recent_requests(ip, timedelta(minutes=1))
        total_hour = self._store.get_requests(ip)

        if len(recent_minute) >= max_per_minute:
            if len(recent_minute) >= max_per_minute * 2:
                self._store.block_fingerprint(fingerprint, FINGERPRINT_BLOCK_DURATION)

            rl_logger.vsilent(
                f"⛔ Per-minute limit hit for {ip} "
                f"[{len(recent_minute)}/{max_per_minute}]"
                + (" [SUSPICIOUS]" if is_suspicious else ""),
                extra={
                    "ip": ip,
                    "count": len(recent_minute),
                    "suspicious": is_suspicious,
                },
            )
            return False

        if len(total_hour) >= max_per_hour:
            rl_logger.vsilent(
                f"⛔ Per-hour limit hit for {ip} "
                f"[{len(total_hour)}/{max_per_hour}]"
                + (" [SUSPICIOUS]" if is_suspicious else ""),
                extra={"ip": ip, "count": len(total_hour), "suspicious": is_suspicious},
            )
            return False

        self._store.add_request(ip, datetime.now())
        return True

    def _is_in_active_cluster(self, ip: str) -> bool:
        if not self._store.is_coordinated_ip(ip):
            return False

        now = datetime.now()
        for cluster in self._store.get_attack_clusters():
            if ip in cluster.ips and now - cluster.last_seen < timedelta(minutes=30):
                rl_logger.vsilent(
                    f"🚫 Blocked coordinated-attack IP: {ip}",
                    extra={"ip": ip, "cluster": cluster.attack_signature[:8]},
                )
                return True

        self._store.discard_coordinated_ip(ip)
        return False

    def _distributed_brute_force_detected(self, ip: str, username: str) -> bool:
        count = self._store.count_ips_with_login_attempts(exclude_ip=ip)
        if count >= 10:
            rl_logger.vsilent(
                f"🚨 Distributed brute-force on '{username}' from {count} IPs",
                extra={"username": username, "ip_count": count},
            )
            return True
        return False
