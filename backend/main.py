import sys
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from backend.api import file_routes
from starlette.requests import Request
import json
import asyncio
from backend.utils.logger import setup_logger

# Thiết lập logger
logger = setup_logger()

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
app.include_router(file_routes.router, prefix="/api", tags=["file-translator"])

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
    logger.info("Home page accessed")
    # Trả về template home.html
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/live-translator", response_class=HTMLResponse)
async def live_translator(request: Request):
    logger.info("Live translator page accessed")
    # Trả về template live_translator.html
    return templates.TemplateResponse("live_translator.html", {"request": request})

@app.get("/file-translator", response_class=HTMLResponse)
async def file_translator(request: Request):
    logger.info("File translator page accessed")
    # Trả về template file_translator.html
    return templates.TemplateResponse("file_translator.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Client connected")
    # Ngôn ngữ mặc định
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
                            source_lang = message.get("source_lang", "auto")
                            target_lang = message.get("target_lang", "vi")

                            # Dịch văn bản
                            translated_text = translate_text(text, source_lang, target_lang)
                            logger.info(f"Translate from {source_lang} to {target_lang}: {text} -> {translated_text}")
                            await websocket.send_json({
                                "type": "translation",
                                "text": str(translated_text),
                                "origin": text
                            })
                        elif message.get("type") == "playText":
                            text = message.get("text","")
                            target_lang = message.get("target_lang", "vi")
                            # Chuyển văn bản thành âm thanh
                            audio = text_to_speech(text,target_lang)
                            logger.info(f"Text to Speech with {target_lang}: {text}")
                            # Mã hóa dữ liệu âm thanh thành base64
                            await websocket.send_json({
                                "type": "audio",
                                "audio": audio,
                                "text": text
                            })
                        elif message.get("type")=="audio":
                            lang = message.get('lang','vi')
                            logger.info(f"Language set to: {lang}")
                    except json.JSONDecodeError:
                        logger.error("Invalid JSON format")
                        await websocket.send_text(f"Echo: {data['text']}")

                elif "bytes" in data:
                    try:
                        audio_data =   data["bytes"]
                        
                        # Chuyển đổi âm thanh thành văn bản
                        text = speech_to_text(audio_data, language=lang )
                        logger.info(f"Speech to Text with {lang}: {audio_data} -> {text}")                       
                        # Gửi kết quả văn bản về phía client
                        await websocket.send_json({
                            "type": "STT",
                            "text": str(text),
                        })
                    except Exception as e:
                        logger.error(f"STT error: {e}")
                        await websocket.send_json({
                        "type": "error",
                        "message": f"Speech-to-text failed: {str(e)}"
                        })
            except asyncio.TimeoutError:
                logger.info("Timeout, sending ping")
                await websocket.send_json({"type": "ping"})
            except WebSocketDisconnect:
                logger.info("Client disconnected")
                break

    except WebSocketDisconnect:
        logger.info("Client disconnected")
        return
    except Exception as e:
        logger.error(f"Error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        logger.info("Closing WebSocket connection")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
