# game/events.py -- tiny subscribe/emit event bus.
# Event names (camelCase): enemyKilled, toolDestroyed, cpuHit
# Add new names freely, but document them here.

_listeners = {}


def subscribe(name, callback):
    """Call callback(*args) whenever `name` is emitted."""
    _listeners.setdefault(name, []).append(callback)


def unsubscribe(name, callback):
    if callback in _listeners.get(name, []):
        _listeners[name].remove(callback)


def emit(name, *args):
    # iterate over a copy so listeners may (un)subscribe while handling
    for callback in list(_listeners.get(name, [])):
        callback(*args)


def clearAll():
    """Drop every listener (use when restarting the game or leaving Lab mode)."""
    _listeners.clear()

