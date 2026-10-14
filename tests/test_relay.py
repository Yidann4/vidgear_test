import numpy as np

import relay
from config import Config
from stages.encode import encode_jpeg
from stages.fanout import unpack

META = {"seq": 3, "stamps": {"capture": 1.0, "sent": 2.0}}
FRAME = np.zeros((48, 64, 3), np.uint8)


def test_raw_frame_is_jpeg_encoded_and_stamped():
    header, jpeg = unpack(relay.to_message(FRAME, META, Config(), t_received=3.0))
    assert header["seq"] == 3
    assert header["stamps"]["received"] == 3.0
    assert header["stamps"]["encoded"] >= header["stamps"]["received"]
    assert jpeg[:2] == b"\xff\xd8"


def test_passthrough_forwards_bytes_untouched():
    jpeg = encode_jpeg(FRAME)
    payload = np.frombuffer(jpeg, np.uint8)
    _, out = unpack(relay.to_message(payload, META, Config(pipeline="passthrough"), t_received=3.0))
    assert out == jpeg
