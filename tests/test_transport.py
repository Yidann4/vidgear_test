"""Loopback NetGear test (real sockets on a private port)."""
import threading

import numpy as np
import pytest

from stages.transport import Receiver, Sender


@pytest.mark.parametrize("jpeg,port", [(False, 5600), (True, 5601)])
def test_frame_and_meta_roundtrip(jpeg, port):
    got = []

    def rx_thread():
        rx = Receiver("127.0.0.1", port, jpeg=jpeg)
        for payload, meta in rx.frames():
            got.append((payload, meta))
        rx.close()

    t = threading.Thread(target=rx_thread)
    t.start()
    tx = Sender("127.0.0.1", port, jpeg=jpeg)
    frame = np.full((48, 64, 3), 100, np.uint8)
    for seq in range(4):
        tx.send(frame, {"seq": seq, "stamps": {"sent": 1.0}})
    tx.close()
    t.join(timeout=20)

    # the final frame can be lost when the sender closes right after sending
    assert [m["seq"] for _, m in got][:3] == [0, 1, 2]
    assert got[0][0].shape == frame.shape


def test_raw_bytes_roundtrip_for_passthrough():
    """Passthrough mode ships pre-encoded JPEG bytes as a 1-D uint8 array, uncompressed."""
    got = []

    def rx_thread():
        rx = Receiver("127.0.0.1", 5602)
        got.extend(rx.frames())
        rx.close()

    t = threading.Thread(target=rx_thread)
    t.start()
    tx = Sender("127.0.0.1", 5602)
    blob = np.frombuffer(b"\xff\xd8" + bytes(range(256)) * 10, np.uint8)
    for seq in range(3):
        tx.send(blob, {"seq": seq, "stamps": {}})
    tx.close()
    t.join(timeout=20)

    assert got[0][0].tobytes() == blob.tobytes()
