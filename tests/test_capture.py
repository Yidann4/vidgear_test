from itertools import islice

from stages.capture import synthetic_frames


def test_synthetic_frames_shape_and_pacing():
    out = list(islice(synthetic_frames(160, 120, 50), 5))  # 20 ms period
    assert out[0][0].shape == (120, 160, 3)
    ts = [t for _, t in out]
    assert all(b > a for a, b in zip(ts, ts[1:]))
    assert 15 < (ts[-1] - ts[0]) / 4 < 60
