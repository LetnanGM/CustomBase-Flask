"""
There's Layer 3 of High-Level Decorator API & Namespace Scoping
"""

from typing import Dict, Set, Optional, Callable, List, Type, Any

from .eventbus import EventBus
from .namespace import _NamespacedBus
from .model import Priority, Event


class EventSystem:
    """
    Layer 3 — Universal entry point.
    Manages multiple named buses + global default bus.
    Provides decorator API similar to Flask/FastAPI routing.
    """

    def __init__(self):
        self._buses: Dict[str, EventBus] = {}
        self._default = self._make_bus("global")

    def _make_bus(self, name: str) -> EventBus:
        bus = EventBus(name=name)
        self._buses[name] = bus
        return bus

    def bus(self, name: str = "global") -> EventBus:
        """Get or create a named bus."""
        if name not in self._buses:
            self._make_bus(name)
        return self._buses[name]

    def namespace(self, ns: str, bus: str = "global") -> _NamespacedBus:
        """Return a namespace-scoped view of a bus."""
        return _NamespacedBus(self.bus(bus), ns)

    # ── Decorator API ─────────────────────────────────────────────

    def on(
        self,
        event_name: str,
        *,
        priority: int = Priority.NORMAL,
        once: bool = False,
        tags: Optional[Set[str]] = None,
        bus: str = "global",
    ):
        """Decorator: @events.on('user.login')"""

        def decorator(fn: Callable):
            self.bus(bus).on(event_name, fn, priority=priority, once=once, tags=tags)
            return fn

        return decorator

    def filter(
        self, event_name: str, *, priority: int = Priority.NORMAL, bus: str = "global"
    ):
        """Decorator: @events.filter('content.render') — like WP add_filter."""

        def decorator(fn: Callable):
            self.bus(bus).on(event_name, fn, priority=priority)
            return fn

        return decorator

    def middleware(self, bus: str = "global"):
        """Decorator: @events.middleware() — register a bus-level interceptor."""

        def decorator(fn: Callable):
            self.bus(bus).use(fn)
            return fn

        return decorator

    # ── Emit shortcuts ────────────────────────────────────────────

    def emit(self, name: str, *, bus: str = "global", **payload) -> Event:
        return self.bus(bus).emit(name, **payload)

    async def emit_async(self, name: str, *, bus: str = "global", **payload) -> Event:
        return await self.bus(bus).emit_async(name, **payload)

    def emit_filter(
        self, name: str, value: Any, *, bus: str = "global", **payload
    ) -> Any:
        return self.bus(bus).emit_filter(name, value, **payload)

    def off(self, name: str, handler=None, *, bus: str = "global"):
        return self.bus(bus).off(name, handler)

    # ── Typed events ──────────────────────────────────────────────

    def typed(self, event_cls: Type[Event]):
        """
        Decorator for typed event handlers.
        @events.typed(UserLoginEvent)
        def handle(event: UserLoginEvent): ...
        Listeners are registered for event_cls.__name__.
        """

        def decorator(fn: Callable):
            self._default.on(event_cls.__name__, fn)
            return fn

        return decorator

    def dispatch(self, event: Event, *, bus: str = "global") -> Event:
        """Fire a pre-built Event object (typed dispatch)."""
        return self.bus(bus).emit(event)

    # ── Utilities ─────────────────────────────────────────────────

    def history(
        self, event_name: Optional[str] = None, *, bus: str = "global"
    ) -> List[Event]:
        return self.bus(bus).history(event_name)

    def __repr__(self):
        return f"<EventSystem buses={list(self._buses.keys())}>"
