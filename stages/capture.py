"""Stage 1: frame source. Yields (frame, t_capture_ms)."""
import itertools
import time

import cv2
import numpy as np

from timing import now


def camera_frames(index, width, height, fps):
    cap = cv2.VideoCapture(index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, fps)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # don't queue stale frames
    if not cap.isOpened():
        raise RuntimeError(f"cannot open camera {index}")
    min_gap = 0.9 * 1000 / fps  # cameras often ignore CAP_PROP_FPS, so drop extra frames here
    last = 0.0
    try:
        while True:
            ok, frame = cap.read()
            t = now()
            if not ok:
                raise RuntimeError("camera read failed")
            if t - last < min_gap:
                continue
            last = t
            yield frame, t
    finally:
        cap.release()


def synthetic_frames(width, height, fps):
    """Moving bar plus frame number. Same output as camera_frames, no hardware."""
    period = 1 / fps
    next_t = time.perf_counter()
    for seq in itertools.count():
        next_t += period
        time.sleep(max(0.0, next_t - time.perf_counter()))
        frame = np.zeros((height, width, 3), np.uint8)
        x = (seq * 8) % width
        cv2.rectangle(frame, (x, 0), (min(x + 40, width - 1), height - 1), (0, 255, 0), -1)
        cv2.putText(frame, str(seq), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        yield frame, now()
