"""Stage 2: NetGear wrappers. `meta` must be JSON-serialisable (NetGear sends it as JSON).

NetGear only delivers `message` to the client in bidirectional mode, which supports
pattern 0 (request/reply) and 1 (pair) but not 2 (pub/sub).
"""
from vidgear.gears import NetGear


def _options(jpeg, quality=80):
    # NetGear enables JPEG compression by default, so always set it explicitly.
    opts = {"bidirectional_mode": True, "jpeg_compression": jpeg}
    if jpeg:
        opts |= {
            "jpeg_compression_quality": quality,
            "jpeg_compression_fastdct": True,
            "jpeg_compression_fastupsample": False,
        }
    return opts


class Sender:
    def __init__(self, host, port, pattern=0, jpeg=False, quality=80):
        self._ng = NetGear(address=host, port=str(port), protocol="tcp", pattern=pattern,
                           logging=False, **_options(jpeg, quality))

    def send(self, payload, meta):
        self._ng.send(payload, message=meta)

    def close(self):
        self._ng.close()


class Receiver:
    def __init__(self, host, port, pattern=0, jpeg=False):
        self._ng = NetGear(address=host, port=str(port), protocol="tcp", pattern=pattern,
                           receive_mode=True, logging=False, **_options(jpeg))

    def frames(self):
        """Yields (payload, meta) until the sender terminates."""
        while (out := self._ng.recv()) is not None:
            meta, payload = out
            yield payload, meta

    def close(self):
        self._ng.close()
