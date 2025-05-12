import sys
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
import json
import asyncio
import base64
# Thêm thư mục chứa translation_service vào path
sys.path.append(str(Path(__file__).parent / "services"))
try:
    from translation_service import translate_text
except ImportError as e:
    print(f"Import error: {e}")
    raise

sys.path.append(str(Path(__file__).parent / "services"))
try:
    from stt_service import speech_to_text
except ImportError as e:
    print(f"Import error: {e}")
    raise

sys.path.append(str(Path(__file__).parent / "services"))
try:
    from tts_service import text_to_speech
except ImportError as e:
    print(f"Import error: {e}")
    raise

# Khởi tạo ứng dụng
app = FastAPI()

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cấu hình thư mục tĩnh và templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# Route chính
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    lang = "vi"
    try:
        while True:
            try:
                # Nhận dữ liệu từ WebSocket với timeout
                data = await asyncio.wait_for(websocket.receive(), timeout=30.0)

                # Kiểm tra loại dữ liệu là text hay audio
                if "text" in data:
                    try:
                        message = json.loads(data["text"])

                        if message.get("type") == "translate":
                            text = message.get("text", "")
                            target_lang = message.get("target_lang", "vi")

                            # Dịch văn bản
                            translated_text = translate_text(text, target_lang)
                            await websocket.send_json({
                                "type": "translation",
                                "text": str(translated_text),
                                "origin": text
                            })
                        elif message.get("type") == "playText":
                            text = message.get("text","")
                            target_lang = message.get("target_lang", "vi")
                            # Chuyển văn bản thành âm thanh
                            audio = text_to_speech(text,lang)
                            # Mã hóa dữ liệu âm thanh thành base64
                            await websocket.send_json({
                                "type": "audio",
                                "audio": audio,
                                "text": text
                            })
                            
                        elif message.get("type")=="audio":
                            lang = message.get('lang','vi')
                    except json.JSONDecodeError:
                        await websocket.send_text(f"Echo: {data['text']}")

                elif "bytes" in data:
                    try:
                        audio_data =   data["bytes"]
                        
                        # Chuyển đổi âm thanh thành văn bản
                        text = speech_to_text(audio_data,language =lang )
                        print('text', text)
                        
                        # Gửi kết quả văn bản về phía client
                        await websocket.send_json({
                            "type": "STT",
                            "text": str(text),
                        })
                    except Exception as e:
                        await websocket.send_json({
                        "type": "error",
                        "message": f"Speech-to-text failed: {str(e)}"
                        })
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "ping"})

    except WebSocketDisconnect:
        print("Client disconnected")
        return
    except Exception as e:
        print(f"Unexpected error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
