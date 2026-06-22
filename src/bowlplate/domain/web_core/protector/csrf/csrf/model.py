from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set

from ....bootstrap import CSRFLogger

__all__ = ["CSRFLogger"]


@dataclass(frozen=True)
class CSRFConf:
    """Simple configuration data"""

    BASE_TOKEN_NUMBER: int = 32


@dataclass
class CSRFViolation:
    """Track CSRF violation attempts"""

    timestamp: datetime
    ip: str
    endpoint: str
    referer: str
    origin: str
    user_agent: str
    token_provided: bool
    token_valid: bool
    severity: int = 1


@dataclass
class TokenMetadata:
    """Metadata for advanced token tracking"""

    token: str = None
    created_at: datetime = None
    ip: str = None
    user_agent: str = None
    usage_count: int = 0
    last_used: Optional[datetime] = None
    is_compromised: bool = False


class _PrivModel:
    # Tracking dictionaries
    violations: List[CSRFViolation] = []
    suspicious_ips: Dict[str, int] = defaultdict(int)
    blocked_ips: Dict[str, datetime] = {}
    token_metadata: Dict[str, TokenMetadata] = {}

    # Attack pattern detection
    csrf_attack_patterns: Dict[str, List[datetime]] = defaultdict(list)
    compromised_tokens: Set[str] = set()

    TOKEN_EXPIRY_HOURS = 2
    MAX_TOKEN_USAGE = 50  # max times a token can be reused
    SUSPICIOUS_THRESHOLD = 3  # Failed attempts before marking as suspicious
