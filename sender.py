"""cv2 capture -> NetGear server."""
import numpy as np

from config import load
from stages.capture import camera_frames, synthetic_frames
from stages.encode import encode_jpeg
from stages.transport import Sender
from timing import now


def open_source(cfg):
    if cfg.source == "synthetic":
        return synthetic_frames(cfg.width, cfg.height, cfg.fps)
    return camera_frames(cfg.camera_index, cfg.width, cfg.height, cfg.fps)


def main():
    cfg = load()
    tx = Sender(cfg.netgear_host, cfg.netgear_port, cfg.netgear_pattern,
                jpeg=cfg.pipeline == "netgear_jpeg", quality=cfg.jpeg_quality)
    try:
        for seq, (frame, t_capture) in enumerate(open_source(cfg)):
            payload = frame
            if cfg.pipeline == "passthrough":
                payload = np.frombuffer(encode_jpeg(frame, cfg.jpeg_quality), np.uint8)
            stamps = {"capture": t_capture, "sent": now()}
            tx.send(payload, {"seq": seq, "stamps": stamps})  # may block (request/reply waits for the relay)
    except KeyboardInterrupt:
        pass
    finally:
        tx.close()


if __name__ == "__main__":
    main()
