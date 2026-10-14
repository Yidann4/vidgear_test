"""Stage 3: BGR frame -> JPEG bytes."""
import cv2


def encode_jpeg(frame, quality=80) -> bytes:
    ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise ValueError("jpeg encode failed")
    return buf.tobytes()
