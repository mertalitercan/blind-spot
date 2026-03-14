"""WebSocket endpoint — pushes real-time fraud alerts to the dashboard."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import store

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/notifications")
async def notifications_ws(websocket: WebSocket):
    """Dashboard connects here to receive real-time fraud alerts."""
    await websocket.accept()
    store.websocket_connections.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep-alive
    except WebSocketDisconnect:
        store.websocket_connections.discard(websocket)
