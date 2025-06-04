import whisper
import tempfile
import subprocess
import os
#from punctuation import restore_punctuation


# Load mô hình Whisper (nhẹ và đủ tốt)
model = whisper.load_model("base")

def convert_webm_to_wav(webm_path: str, wav_path: str):
    subprocess.run(["ffmpeg", "-y", "-i", webm_path, wav_path], check=True)

def speech_to_text(audio_bytes: bytes, language: str = "vi") -> str:
    try:
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f_webm:
            f_webm.write(audio_bytes)
            f_webm.flush()
            webm_path = f_webm.name

        wav_path = webm_path.replace(".webm", ".wav")
        convert_webm_to_wav(webm_path, wav_path)

        # Truyền tham số language để Whisper dùng đúng ngôn ngữ
        result = model.transcribe(wav_path, task="transcribe", language=language)
        raw_text = result["text"]
        
        os.remove(webm_path)
        os.remove(wav_path)

        return raw_text

    except Exception as e:
        print(f"Lỗi chuyển âm thanh sang văn bản: {e}")
        return "[Lỗi chuyển âm thanh]"

    