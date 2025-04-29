from fastapi import WebSocket

# WebSocket route cho truyền tải dữ liệu
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message received: {data}")
