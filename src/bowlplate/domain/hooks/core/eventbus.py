# ─────────────────────────────────────────────────────────────────
# LAYER 1 — Core EventBus
# ─────────────────────────────────────────────────────────────────

import asyncio
import threading
import weakref
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Set, Union

from .model import Event, Priority, PropagationError, _HandlerRecord, logger


class EventBus:
    """
    Thread-safe, priority-based event bus.
    Supports sync and async listeners, wildcards, namespaces,
    middleware (interceptors), and weak references.
    """

    def __init__(self, name: str = "default"):
        self.name = name
        self._lock = threading.RLock()
        self._listeners: Dict[str, List[_HandlerRecord]] = defaultdict(list)
        self._middleware: List[Callable] = []  # pre-fire interceptors
        self._history: List[Event] = []  # replay log
        self._max_history = 200
        self._counter = 0  # insertion-order counter

    # ── Registration ─────────────────────────────────────────────

    def on(
        self,
        event_name: str,
        handler: Callable,
        *,
        priority: int = Priority.NORMAL,
        once: bool = False,
        tags: Optional[Set[str]] = None,
        weak: bool = False,
    ) -> "EventBus":
        """Register a listener. Returns self for chaining."""
        with self._lock:
            self._counter += 1
            record = _HandlerRecord(
                priority=priority,
                order=self._counter,
                handler=handler,
                once=once,
                tags=tags or set(),
                weak=weak,
            )
            if weak:
                # store bound-method via weakref
                try:
                    record._ref = weakref.WeakMethod(handler)
                except TypeError:
                    record._ref = weakref.ref(handler)
                record.handler = (
                    handler.__func__ if hasattr(handler, "__func__") else handler
                )

            self._listeners[event_name].append(record)
            self._listeners[event_name].sort(key=lambda r: (r.priority, r.order))
        logger.debug(
            "[%s] registered '%s' → %s (prio=%d)",
            self.name,
            event_name,
            handler,
            priority,
        )
        return self

    def once(self, event_name: str, handler: Callable, **kwargs) -> "EventBus":
        """Register a one-shot listener."""
        return self.on(event_name, handler, once=True, **kwargs)

    def off(self, event_name: str, handler: Optional[Callable] = None) -> "EventBus":
        """Remove one or all listeners for event_name."""
        with self._lock:
            if handler is None:
                self._listeners.pop(event_name, None)
            else:
                self._listeners[event_name] = [
                    r for r in self._listeners[event_name] if r.handler is not handler
                ]
        return self

    def off_by_tag(self, tag: str) -> "EventBus":
        """Remove all listeners carrying a specific tag."""
        with self._lock:
            for key in list(self._listeners):
                self._listeners[key] = [
                    r for r in self._listeners[key] if tag not in r.tags
                ]
        return self

    # ── Middleware ────────────────────────────────────────────────

    def use(self, middleware: Callable) -> "EventBus":
        """
        Add middleware. Signature: middleware(event, next) -> Any
        Like Express.js / Koa middleware chains.
        Call next(event) to continue, skip it to intercept.
        """
        self._middleware.append(middleware)
        return self

    # ── Firing ───────────────────────────────────────────────────

    def emit(self, event: Union[str, Event], **payload) -> Event:
        """
        Fire a sync event. Runs all matching listeners in priority order.
        Wildcards: 'user.*' matches 'user.login', 'user.logout', etc.
        Returns the Event object (with .results collected).
        """
        if isinstance(event, str):
            event = Event(name=event, payload=payload, namespace=self.name)

        # run middleware chain
        event = self._run_middleware(event)
        if event is None:
            return Event(name="intercepted")

        # collect matching listener lists (exact + wildcards)
        records = self._collect_records(event.name)

        # store history
        with self._lock:
            self._history.append(event)
            if len(self._history) > self._max_history:
                self._history.pop(0)

        dead = []
        for record in records:
            if event.stopped:
                break
            if not record.is_alive():
                dead.append(record)
                continue
            try:
                result = record.call(event)
                event._results.append(result)
                if record.once:
                    dead.append(record)
            except PropagationError:
                event.stop_propagation()
                break
            except Exception as exc:
                logger.error(
                    "[%s] handler error on '%s': %s",
                    self.name,
                    event.name,
                    exc,
                    exc_info=True,
                )

        # cleanup dead / one-shot records
        if dead:
            with self._lock:
                for key in self._listeners:
                    self._listeners[key] = [
                        r for r in self._listeners[key] if r not in dead
                    ]

        return event

    async def emit_async(self, event: Union[str, Event], **payload) -> Event:
        """
        Fire an event, awaiting async listeners concurrently (gather).
        Sync listeners run in a thread pool so they don't block the loop.
        """
        if isinstance(event, str):
            event = Event(name=event, payload=payload, namespace=self.name)

        event = self._run_middleware(event)
        if event is None:
            return Event(name="intercepted")

        records = self._collect_records(event.name)
        loop = asyncio.get_event_loop()

        async def _call(record):
            if not record.is_alive():
                return None
            try:
                if asyncio.iscoroutinefunction(record.handler):
                    return await record.call(event)
                else:
                    return await loop.run_in_executor(None, lambda: record.call(event))
            except PropagationError:
                event.stop_propagation()
            except Exception as exc:
                logger.error(
                    "[%s] async handler error on '%s': %s",
                    self.name,
                    event.name,
                    exc,
                    exc_info=True,
                )

        results = await asyncio.gather(*[_call(r) for r in records])
        event._results.extend(r for r in results if r is not None)
        return event

    def emit_filter(self, event_name: str, value: Any, **payload) -> Any:
        """
        WordPress apply_filters()-style: pass a value through all listeners.
        Each listener receives (event) and its return value replaces event['value'].
        Returns the final transformed value.
        """
        event = Event(
            name=event_name, payload={"value": value, **payload}, namespace=self.name
        )
        records = self._collect_records(event_name)
        for record in records:
            if event.stopped:
                break
            try:
                result = record.call(event)
                if result is not None:
                    event["value"] = result
            except Exception as exc:
                logger.error(
                    "[%s] filter error on '%s': %s",
                    self.name,
                    event_name,
                    exc,
                    exc_info=True,
                )
        return event["value"]

    # ── Helpers ───────────────────────────────────────────────────

    def _collect_records(self, event_name: str) -> List[_HandlerRecord]:
        """Collect exact-match + wildcard listeners, sorted by priority."""
        with self._lock:
            exact = list(self._listeners.get(event_name, []))
            wildcards = []
            for pattern, records in self._listeners.items():
                if "*" in pattern and self._matches(pattern, event_name):
                    wildcards.extend(records)
            combined = exact + wildcards
            combined.sort(key=lambda r: (r.priority, r.order))
        return combined

    @staticmethod
    def _matches(pattern: str, name: str) -> bool:
        """Simple glob: 'user.*' matches 'user.login'."""
        parts_p = pattern.split(".")
        parts_n = name.split(".")
        if len(parts_p) != len(parts_n):
            return False
        return all(p == n or p == "*" for p, n in zip(parts_p, parts_n))

    def _run_middleware(self, event: Event) -> Optional[Event]:
        """Chain middleware. Returns None if intercepted."""
        idx = [-1]

        def next_mw(ev):
            idx[0] += 1
            if idx[0] < len(self._middleware):
                return self._middleware[idx[0]](ev, next_mw)
            return ev

        return next_mw(event)

    # ── Introspection ─────────────────────────────────────────────

    def listeners(self, event_name: str) -> List[Callable]:
        with self._lock:
            return [r.handler for r in self._listeners.get(event_name, [])]

    def events(self) -> List[str]:
        with self._lock:
            return list(self._listeners.keys())

    def history(self, event_name: Optional[str] = None) -> List[Event]:
        """Return recent fired events, optionally filtered by name."""
        if event_name:
            return [e for e in self._history if e.name == event_name]
        return list(self._history)

    def clear(self, event_name: Optional[str] = None):
        with self._lock:
            if event_name:
                self._listeners.pop(event_name, None)
            else:
                self._listeners.clear()

    def __repr__(self):
        return f"<EventBus name={self.name!r} events={len(self._listeners)}>"
