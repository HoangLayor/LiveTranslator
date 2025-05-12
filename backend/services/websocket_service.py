# websocket_service.py - Placeholder file
from fastapi import WebSocket
from backend.services.stt_service import speech_to_text
from backend.services.translation_service import translate_text
from backend.services.tts_service import text_to_speech

async def handle_ws_connection(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            audio_bytes = await websocket.receive_bytes()
            text = speech_to_text(audio_bytes)
            translated = translate_text(text, target_lang="vi")
            audio_response = text_to_speech(translated)
            await websocket.send_bytes(audio_response)
    except Exception as e:
        await websocket.close()