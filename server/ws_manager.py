import json

from fastapi import WebSocket
from typing import Dict, Set

from fastapi.encoders import jsonable_encoder


class WebSocketManager:
    """
    Manages websocket connections grouped by channel (event_id).
    """

    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, channel: str, websocket: WebSocket):
        await websocket.accept()
        self._connections.setdefault(channel, set()).add(websocket)

        print(
            f"🔌 WS CONNECT | channel={channel} | "
            f"connections={len(self._connections[channel])}"
        )

    def disconnect(self, channel: str, websocket: WebSocket):
        if channel in self._connections:
            self._connections[channel].discard(websocket)

            print(
                f"❌ WS DISCONNECT | channel={channel} | "
                f"connections={len(self._connections[channel])}"
            )

            if not self._connections[channel]:
                del self._connections[channel]
                print(f"🧹 WS CHANNEL EMPTY | channel={channel}")

    async def broadcast(self, channel: str, payload: dict):
        if channel not in self._connections:
            return

        # ✅ Convert datetimes + Pydantic models safely
        encoded = jsonable_encoder(payload)
        message = json.dumps(encoded)

        dead = set()

        for ws in self._connections[channel]:
            try:
                await ws.send_text(message)
            except Exception:
                dead.add(ws)

        for ws in dead:
            self.disconnect(channel, ws)