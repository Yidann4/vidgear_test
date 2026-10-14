import time


def now() -> float:
    """Wall-clock epoch milliseconds. Comparable with the browser's
    performance.timeOrigin + performance.now() when on the same machine."""
    return time.time() * 1000
