import cv2
import numpy as np

from stages.encode import encode_jpeg


def test_roundtrip_shape():
    frame = np.full((48, 64, 3), 128, np.uint8)
    jpeg = encode_jpeg(frame)
    assert jpeg[:2] == b"\xff\xd8"
    assert cv2.imdecode(np.frombuffer(jpeg, np.uint8), cv2.IMREAD_COLOR).shape == frame.shape


def test_lower_quality_is_smaller():
    frame = np.random.default_rng(0).integers(0, 255, (120, 160, 3), dtype=np.uint8)
    assert len(encode_jpeg(frame, 30)) < len(encode_jpeg(frame, 95))
