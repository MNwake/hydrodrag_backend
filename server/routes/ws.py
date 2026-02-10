import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from core.controllers.score_broadcaster import ws_manager

router = APIRouter(prefix="/ws", tags=["WebSockets"])



@router.websocket("/events/{event_id}")
async def event_ws(websocket: WebSocket, event_id: str):
    channel = f"event:{event_id}"

    print(f"🔌 WS CONNECT REQUEST | channel={channel}")
    await ws_manager.connect(channel, websocket)

    try:
        while True:
            await websocket.receive()
    except (WebSocketDisconnect, RuntimeError):
        # RuntimeError happens after disconnect frame
        pass
    finally:
        ws_manager.disconnect(channel, websocket)
        print(f"❌ WS DISCONNECT | channel={channel}")