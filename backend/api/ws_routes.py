from fastapi import APIRouter, WebSocket

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("WebSocket connected successfully.")
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")
