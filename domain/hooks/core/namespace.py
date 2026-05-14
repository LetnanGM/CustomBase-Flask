from .eventbus import EventBus

class _NamespacedBus:
    """
    A view over an EventBus that auto-prefixes all event names.
    Like WordPress plugin namespacing: 'myplugin/user_login'.
    """

    def __init__(self, bus: EventBus, namespace: str):
        self._bus = bus
        self._ns  = namespace

    def _qualify(self, name: str) -> str:
        return f"{self._ns}.{name}" if not name.startswith(self._ns) else name

    def on(self, name, handler, **kw):
        return self._bus.on(self._qualify(name), handler, **kw)

    def once(self, name, handler, **kw):
        return self._bus.once(self._qualify(name), handler, **kw)

    def off(self, name, handler=None):
        return self._bus.off(self._qualify(name), handler)

    def emit(self, name, **payload):
        return self._bus.emit(self._qualify(name), **payload)

    async def emit_async(self, name, **payload):
        return await self._bus.emit_async(self._qualify(name), **payload)

    def emit_filter(self, name, value, **payload):
        return self._bus.emit_filter(self._qualify(name), value, **payload)

    def namespace(self, sub: str) -> "_NamespacedBus":
        return _NamespacedBus(self._bus, f"{self._ns}.{sub}")

