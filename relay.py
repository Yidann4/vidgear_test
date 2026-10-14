"""NetGear client -> JPEG (unless passthrough) -> WebSocket broadcast + static page."""
import asyncio
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from config import load
from stages.encode import encode_jpeg
from stages.fanout import Hub, pack
from stages.transport import Receiver
from timing import now

cfg = load()
hub = Hub()


def to_message(payload, meta, cfg, t_received) -> bytes:
    stamps = {**meta["stamps"], "received": t_received}
    jpeg = payload.tobytes() if cfg.pipeline == "passthrough" else encode_jpeg(payload, cfg.jpeg_quality)
    stamps["encoded"] = now()
    return pack({"seq": meta["seq"], "stamps": stamps}, jpeg)


def receive_loop(loop):
    while True:  # survive sender restarts
        rx = Receiver(cfg.netgear_host, cfg.netgear_port, cfg.netgear_pattern,
                      jpeg=cfg.pipeline == "netgear_jpeg")
        try:
            for payload, meta in rx.frames():
                t_received = now()
                loop.call_soon_threadsafe(hub.publish, to_message(payload, meta, cfg, t_received))
        finally:
            rx.close()
        time.sleep(1)


@asynccontextmanager
async def lifespan(app):
    threading.Thread(target=receive_loop, args=(asyncio.get_running_loop(),), daemon=True).start()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def index():
    return FileResponse(Path(__file__).parent / "index.html")


@app.websocket("/ws")
async def ws(ws: WebSocket):
    await ws.accept()
    q = hub.subscribe()
    try:
        while True:
            await ws.send_bytes(await q.get())
    except (WebSocketDisconnect, RuntimeError):
        pass
    finally:
        hub.unsubscribe(q)


if __name__ == "__main__":
    uvicorn.run(app, host=cfg.ws_host, port=cfg.ws_port, log_level="warning")
