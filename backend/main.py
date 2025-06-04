import sys
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from backend.api import file_routes, feedback_routes
from starlette.requests import Request
import json
import asyncio
from backend.utils.logger import setup_logger
from backend.database import engine
from backend.models.feedback_model import Base
import base64

# Import hai hàm PUNCTUATION
from backend.services.punctuation import restore_punctuation, capitalize_after_punctuation

# Initialize database
Base.metadata.create_all(bind=engine)

# Thiết lập logger
logger = setup_logger()

# Thêm đường dẫn services vào sys.path để import các service khác (translate, stt, tts)
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

def handle_audio(base64_audio_str: str):
    audio_bytes = base64.b64decode(base64_audio_str)
    result = speech_to_text(audio_bytes)
    return result

# === TẠO ỨNG DỤNG FASTAPI ===
app = FastAPI()

# Include các router HTTP nếu có
app.include_router(file_routes.router, prefix="/api", tags=["file-translator"])
app.include_router(feedback_routes.router, prefix="/api", tags=["feedback"])

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cấu hình static files & templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# === ROUTES GET CHUYÊN BIỆT ===
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    logger.info("Home page accessed")
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/live-translator", response_class=HTMLResponse)
async def live_translator(request: Request):
    # logger.info("Live translator page accessed")
    return templates.TemplateResponse("live_translator.html", {"request": request})

@app.get("/live-camera", response_class=HTMLResponse)
async def live_translator(request: Request):
    logger.info("Live translator page accessed")
    return templates.TemplateResponse("live_camera.html", {"request": request})

@app.get("/file-translator", response_class=HTMLResponse)
async def file_translator(request: Request):
    # logger.info("File translator page accessed")
    return templates.TemplateResponse("file_translator.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    # logger.info("About page accessed")
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    # logger.info("Contact page accessed")
    return templates.TemplateResponse("contact.html", {"request": request})


# === WEBSOCKET ENDPOINT ===
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Client connected via WebSocket")
    # Ngôn ngữ mặc định (dùng cho STT hoặc TTS)
    lang = "vi"

    try:
        while True:
            try:
                # Chờ client gửi text (JSON string) trong 30s
                raw = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                # Nếu 30s không có message, gửi ping để giữ kết nối
                try:
                    await websocket.send_json({"type": "ping"})
                except WebSocketDisconnect:
                    # Nếu client đã ngắt lúc ping, thoát vòng lặp
                    break
                continue
            except WebSocketDisconnect:
                # Client đóng kết nối
                logger.info("Client disconnected (during receive)")
                break

            # Nếu nhận được raw text, parse JSON
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                # Nếu JSON sai định dạng, gửi text lỗi rồi tiếp tục
                try:
                    await websocket.send_text(f"Invalid JSON: {raw}")
                except WebSocketDisconnect:
                    pass
                continue

            msg_type = message.get("type")

            # ----------------------------
            # 1) PUNCTUATION (chèn dấu câu + viết hoa)
            #    Client phải gửi: { "type": "punctuation", "text": "<chuỗi chưa có dấu>" }
            #    Server trả về:   { "type": "punctuated", "text": "<chuỗi đã có dấu câu>" }
            # ----------------------------
            if msg_type == "punctuation":
                original = message.get("text", "").strip()
                if not original:
                    try:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Empty text field for punctuation"
                        })
                    except WebSocketDisconnect:
                        pass
                    continue

                # 1.a) Phục hồi dấu câu
                punctuated = restore_punctuation(original)
                # 1.b) Viết hoa sau dấu câu
                normalized = capitalize_after_punctuation(punctuated)

                try:
                    await websocket.send_json({
                        "type": "punctuation",
                        "text": normalized
                    })
                except WebSocketDisconnect:
                    break

            # ----------------------------
            # 2) TRANSLATION (dịch văn bản)
            #    Client gửi: { "type": "translate", "text": "...", "source_lang": "...", "target_lang": "..." }
            #    Server trả: { "type": "translation", "text": "<kết quả dịch>", "origin": "<text gốc>" }
            # ----------------------------
            elif msg_type == "translate":
                text_to_translate = message.get("text", "")
                source_lang = message.get("source_lang", "auto")
                target_lang = message.get("target_lang", "vi")

                try:
                    translated_text = translate_text(text_to_translate, source_lang, target_lang)
                    logger.info(f"Translate [{source_lang}→{target_lang}]: {text_to_translate} → {translated_text}")
                    await websocket.send_json({
                        "type": "translation",
                        "text": str(translated_text),
                        "origin": text_to_translate
                    })
                except Exception as e:
                    logger.error(f"Translation error: {e}")
                    try:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Translation failed: {e}"
                        })
                    except WebSocketDisconnect:
                        pass

            # ----------------------------
            # 3) TEXT-TO-SPEECH
            #    Client gửi: { "type": "playText", "text": "...", "target_lang": "..." }
            #    Server trả: { "type": "audio", "audio": <bytes base64>, "text": "<gốc>" }
            # ----------------------------
            elif msg_type == "playText":
                text_to_play = message.get("text", "")
                target_lang = message.get("target_lang", "vi")
                try:
                    audio_bytes = text_to_speech(text_to_play, target_lang)
                    logger.info(f"TTS [{target_lang}]: {text_to_play}")
                    await websocket.send_json({
                        "type": "audio",
                        "audio": audio_bytes,
                        "text": text_to_play
                    })
                except Exception as e:
                    logger.error(f"TTS error: {e}")
                    try:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"TTS failed: {e}"
                        })
                    except WebSocketDisconnect:
                        pass

            # ----------------------------
            # 4) SPEECH-TO-TEXT (nếu bạn dùng binary audio frames)
            #    Client có thể gửi: { "type": "whisper", "audio_base64": "..." }
            #    (Hoặc kết hợp receive_bytes nếu không qua JSON)
            #    Server trả: { "type": "STT", "text": "<kết quả>", ... }
            # ----------------------------
            elif msg_type == "whisper":
                base64_audio = message.get("audio", "")
                logger.info(f"base64_audio from phone: {base64_audio}")
                language = message.get("language","")
                logger.info(f"language from phone: {language}")
                if not base64_audio:
                    try:
                        await websocket.send_json({
                            "type": "error",
                            "message": "No audio_base64 field provided"
                        })
                    except WebSocketDisconnect:
                        pass
                    continue

                try:
                    audio_bytes = base64.b64decode(base64_audio)
                    text = speech_to_text(audio_bytes,language)
                    logger.info(f"STT result: {text}")
                    await websocket.send_json({
                        "type": "Whisper_result",
                        "text": str(text)
                    })
                except Exception as e:
                    logger.error(f"STT error: {e}")
                    try:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Speech-to-text failed: {e}"
                        })
                    except WebSocketDisconnect:
                        pass
            # ----------------------------
            # 5) Tranlation Image (Dịch hình ảnh)
            # Client client {"type": "image","image": base64Image, "source_lang": sourceLanguage,"target_lang": targetLanguage}
            # Server trả về {"type": "translation-image","text": ?,"x": ?,"y": ?}
            # ----------------------------
            elif msg_type == "image":
                print()
                
            elif msg_type == "ping":
                try:
                    await websocket.send_json({"type": "pong"})
                except WebSocketDisconnect:
                    break
            else:
                try:
                    await websocket.send_json({
                        "type": "echo",
                        "text": f"Unknown type: {msg_type}"
                    })
                except WebSocketDisconnect:
                    break

    except WebSocketDisconnect:
        logger.info("Client disconnected (outer WebSocketDisconnect)")
        return

    except Exception as e:
        # Bắt các lỗi bất ngờ khác
        logger.error(f"Unexpected WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass

    finally:
        # Đóng WebSocket nếu chưa đóng
        try:
            await websocket.close()
        except:
            pass


# Nếu chạy main.py trực tiếp:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
