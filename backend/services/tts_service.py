from gtts import gTTS
from io import BytesIO
import base64

def text_to_speech(text: str, lang: str = "vi") -> str:
    """Chuyển text thành giọng nói, trả về base64"""
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return base64.b64encode(audio_buffer.read()).decode('utf-8')
    except Exception as e:
        print(f"TTS Error: {e}")
        return None