"""
              ADVANCED LAYERED EVENT SYSTEM                       
   Inspired by WordPress hooks, Google Guava EventBus,            
   Yandex's internal pubsub, and Django signals                   
                                                                  
   ARCHITECTURE (3 layers):                                       
    Layer 1 — Core Bus        : low-level fire/register + priority   
    Layer 2 — Event Objects   : typed, structured event data         
    Layer 3 — High-Level API  : decorators, namespaces, middleware   

"""

from __future__ import annotations

import asyncio
import logging
from typing import Callable

from .event import EventSystem
from .eventbus import EventBus
from .model import (Event, Priority, PropagationError)

__all__ = ["Event", "Priority", "PropagationError", "EventBus", "EventSystem"]

# Singleton — drop-in replacement for old events.py
events = EventSystem()

# Backwards-compatible shim
def register_hook(event_name: str, callback: Callable, priority: int = Priority.NORMAL):
    events.bus().on(event_name, callback, priority=priority)

def fire_hook(event_name: str, *args, **kwargs) -> Event:
    # pack positional args into payload for compatibility
    payload = kwargs
    if args:
        payload["args"] = args
        
    return events.emit(event_name, **payload)


# USAGE > shows all layers in action
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

    # ── Built-in middleware (logging) ─────────────────────────────
    @events.middleware()
    def log_all(event: Event, next_fn):
        print(f"\n  [MW] Intercepted: {event.name}")
        return next_fn(event)

    # ── Namespace: 'auth' ─────────────────────────────────────────
    auth = events.namespace("auth")
    auth.on("login", lambda e: print(f"  [auth.login] user={e.get('user')}"))

    # ── Decorator API ─────────────────────────────────────────────
    @events.on("user.login", priority=Priority.HIGH)
    def greet(event: Event):
        print(f"  [HIGH] Hello, {event['user']}!")

    @events.on("user.login", priority=Priority.LOW)
    def audit(event: Event):
        print(f"  [LOW]  Audit log: {event['user']} at {event.timestamp:.2f}")

    # ── Wildcard ──────────────────────────────────────────────────
    @events.on("user.*")
    def catch_all(event: Event):
        print(f"  [*]    Caught user event: {event.name}")

    # ── Filter chain (like WP apply_filters) ──────────────────────
    @events.filter("content.render")
    def add_prefix(event: Event):
        return "[SITE] " + event["value"]

    @events.filter("content.render", priority=Priority.LOW)
    def add_suffix(event: Event):
        return event["value"] + " ✓"

    # ── One-shot ──────────────────────────────────────────────────
    @events.on("app.start", once=True)
    def on_start(event: Event):
        print("  [once] App started — this fires only ONCE")

    # ── FIRE ──────────────────────────────────────────────────────
    print("\n═══ EMIT: user.login ═══")
    result = events.emit("user.login", user="alice")
    print(f"  Results collected: {result.results}")

    print("\n═══ EMIT: user.logout ═══")
    events.emit("user.logout", user="alice")

    print("\n═══ EMIT FILTER: content.render ═══")
    rendered = events.emit_filter("content.render", "Hello World")
    print(f"  Final value: {rendered!r}")

    print("\n═══ EMIT: app.start (x2, only fires once) ═══")
    events.emit("app.start")
    events.emit("app.start")   # silent

    print("\n═══ NAMESPACED: auth.login ═══")
    auth.emit("login", user="bob")

    print("\n═══ HISTORY ═══")
    for ev in events.history():
        print(f"  {ev.name:30s} id={ev.event_id[:8]}")

    print("\n═══ ASYNC (event loop) ═══")
    async def demo_async():
        async def async_handler(event: Event):
            await asyncio.sleep(0.01)
            print(f"  [async] Got {event.name} — user={event.get('user')}")
        events.bus().on("user.signup", async_handler)
        await events.emit_async("user.signup", user="carol")
    asyncio.run(demo_async())

    print("\n═══ BACKWARDS COMPAT ═══")
    register_hook("legacy.event", lambda e: print(f"  [legacy] got: {e.payload}"))
    fire_hook("legacy.event", status="ok")

    print("\nDone ✓")
