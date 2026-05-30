"""
SIMPLE Event
it will evolve :D
"""

from collections import defaultdict

_hooks = defaultdict(list)


def register_hook(event_name: str, callback):
    """ """
    _hooks[event_name].append(callback)


def fire_hook(event_name: str, *args, **kwargs):
    """ """
    for callback in _hooks.get(event_name, []):
        try:
            callback(*args, **kwargs)
        except Exception as e:
            print(f"Hook error in {event_name}: {e}")
