"""Time stages in isolation, no network: `pixi run bench` (CAM_SOURCE=synthetic to skip the camera)."""
import statistics
import time
from itertools import islice

from config import load
from sender import open_source
from stages.encode import encode_jpeg
from stages.fanout import pack

N = 200


def bench(name, fn):
    ts = []
    for _ in range(N):
        t = time.perf_counter()
        fn()
        ts.append((time.perf_counter() - t) * 1000)
    ts.sort()
    print(f"{name:14} mean {statistics.mean(ts):6.2f} ms   p95 {ts[int(N * .95)]:6.2f} ms")


cfg = load()
(frame, _), = islice(open_source(cfg), 3, 4)  # skip camera warm-up frames
print(f"{frame.shape[1]}x{frame.shape[0]} q={cfg.jpeg_quality}")
jpeg = encode_jpeg(frame, cfg.jpeg_quality)
print(f"jpeg size: {len(jpeg) / 1024:.0f} KiB, raw size: {frame.nbytes / 1024:.0f} KiB")
bench("jpeg encode", lambda: encode_jpeg(frame, cfg.jpeg_quality))
bench("ws pack", lambda: pack({"seq": 0, "stamps": {}}, jpeg))
