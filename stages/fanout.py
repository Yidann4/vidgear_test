"""Stage 4: one producer -> many WebSocket clients, latest frame only.

Wire format (binary message): 4-byte big-endian header length | JSON header | JPEG bytes
"""
import asyncio
import json
import struct


def pack(header: dict, jpeg: bytes) -> bytes:
    h = json.dumps(header, separators=(",", ":")).encode()
    return struct.pack(">I", len(h)) + h + jpeg


def unpack(message: bytes):
    (n,) = struct.unpack(">I", message[:4])
    return json.loads(message[4:4 + n]), message[4 + n:]


class Hub:
    """Each subscriber gets a 1-slot queue: a slow client skips frames instead of lagging."""

    def __init__(self):
        self._queues: set[asyncio.Queue] = set()

    def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue(maxsize=1)
        self._queues.add(q)
        return q

    def unsubscribe(self, q):
        self._queues.discard(q)

    def publish(self, message: bytes):
        for q in self._queues:
            if q.full():
                q.get_nowait()
            q.put_nowait(message)
