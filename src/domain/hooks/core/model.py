# ─────────────────────────────────────────────────────────────────
# LAYER 0 — Primitives
# ─────────────────────────────────────────────────────────────────
from typing import Any, Callable, Dict, List, Optional, Set

import time
import uuid
import logging

from dataclasses import dataclass, field
from enum import IntEnum

logger = logging.getLogger(__name__)


class Priority(IntEnum):
    """WordPress-style numeric priorities (lower = earlier)."""

    FIRST = -100
    HIGH = -10
    NORMAL = 0
    LOW = 10
    LAST = 100


class PropagationError(Exception):
    """Raised to stop event propagation (like stopPropagation in JS)."""


@dataclass
class Event:
    """
    Layer 2 — Structured event object.
    All events carry metadata + a mutable payload.
    Inspired by Google Guava's EventBus and DOM Events.
    """

    name: str
    payload: Dict[str, Any] = field(default_factory=dict)
    source: Optional[object] = None  # who fired it
    timestamp: float = field(default_factory=time.time)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    namespace: str = "global"
    tags: Set[str] = field(default_factory=set)

    # mutable state
    _stopped: bool = field(default=False, repr=False)
    _results: List[Any] = field(default_factory=list, repr=False)

    def stop_propagation(self):
        """Halt further listener calls for this event."""
        self._stopped = True

    @property
    def stopped(self) -> bool:
        return self._stopped

    @property
    def results(self) -> List[Any]:
        """Collected return values from all listeners (like WP apply_filters)."""
        return self._results

    # Convenience helpers
    def __getitem__(self, key):
        return self.payload[key]

    def __setitem__(self, key, value):
        self.payload[key] = value

    def get(self, key, default=None):
        return self.payload.get(key, default)


@dataclass(order=True)
class _HandlerRecord:
    """Internal: one registered listener."""

    priority: int
    order: int = field(compare=True)  # insertion order tie-break
    handler: Callable = field(compare=False)
    once: bool = field(default=False, compare=False)
    tags: Set[str] = field(default_factory=set, compare=False)
    weak: bool = field(default=False, compare=False)
    _ref: Any = field(default=None, repr=False, compare=False)

    def is_alive(self) -> bool:
        if not self.weak:
            return True
        return self._ref() is not None

    def call(self, *args, **kwargs):
        if self.weak:
            obj = self._ref()
            if obj is None:
                return None
            return self.handler(obj, *args, **kwargs)
        return self.handler(*args, **kwargs)
