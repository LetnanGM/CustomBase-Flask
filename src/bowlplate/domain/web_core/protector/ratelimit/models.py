from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Set


@dataclass
class RequestPattern:
    """Track request patterns for anomaly detection."""

    timestamps: List[datetime] = field(default_factory=list)
    endpoints: List[str] = field(default_factory=list)
    user_agents: Set[str] = field(default_factory=set)
    request_signatures: List[str] = field(default_factory=list)

    MAX_HISTORY = 100

    def record(
        self, timestamp: datetime, endpoint: str, user_agent: str, signature: str
    ):
        self.timestamps.append(timestamp)
        self.endpoints.append(endpoint)
        self.user_agents.add(user_agent)
        self.request_signatures.append(signature)
        self._trim()

    def _trim(self):
        if len(self.timestamps) > self.MAX_HISTORY:
            self.timestamps = self.timestamps[-self.MAX_HISTORY :]
            self.endpoints = self.endpoints[-self.MAX_HISTORY :]
            self.request_signatures = self.request_signatures[-self.MAX_HISTORY :]

    def get_entropy_score(self) -> float:
        """Calculate pattern entropy (lower = more suspicious)."""
        if not self.timestamps:
            return 1.0

        if len(self.timestamps) >= 3:
            intervals = [
                (self.timestamps[i + 1] - self.timestamps[i]).total_seconds()
                for i in range(len(self.timestamps) - 1)
            ]
            avg = sum(intervals) / len(intervals)
            variance = sum((x - avg) ** 2 for x in intervals) / len(intervals)
            if variance < 0.1:
                return 0.3

        endpoint_diversity = len(set(self.endpoints)) / max(len(self.endpoints), 1)
        ua_diversity = len(self.user_agents) / max(len(self.timestamps), 1)
        return (endpoint_diversity + ua_diversity) / 2


@dataclass
class AttackCluster:
    """Represents a group of IPs sharing an attack signature."""

    ips: Set[str] = field(default_factory=set)
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    attack_signature: str = ""
    severity: int = 0

    def update(self, ips: Set[str]):
        self.ips.update(ips)
        self.last_seen = datetime.now()
        self.severity += 1
