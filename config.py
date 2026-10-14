"""All settings in one place. Override any field with a CAM_<FIELD> env var,
e.g. `CAM_FPS=30 CAM_WIDTH=1280 CAM_HEIGHT=720 pixi run sender`."""
import os
from dataclasses import dataclass, fields


@dataclass(frozen=True)
class Config:
    source: str = "camera"        # camera | synthetic (no webcam, isolates the rest of the pipeline)
    camera_index: int = 0
    width: int = 640
    height: int = 480
    fps: int = 15
    jpeg_quality: int = 80
    # raw:          NetGear sends raw frames, relay JPEG-encodes once
    # netgear_jpeg: NetGear JPEG-compresses/decompresses, relay JPEG-encodes again
    # passthrough:  sender JPEG-encodes once, NetGear carries the bytes, relay forwards untouched
    pipeline: str = "raw"
    netgear_host: str = "127.0.0.1"
    netgear_port: int = 5555
    netgear_pattern: int = 0      # 0 request/reply, 1 pair (2 pub/sub can't carry the timing metadata)
    ws_host: str = "0.0.0.0"      # reachable from the local network
    ws_port: int = 8000


def load() -> Config:
    env = {f.name: f.type(os.environ[f"CAM_{f.name.upper()}"])
           for f in fields(Config) if f"CAM_{f.name.upper()}" in os.environ}
    return Config(**env)
