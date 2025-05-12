import whisper
import tempfile
import subprocess
import os

# Load mô hình Whisper
model = whisper.load_model("base")

def convert_webm_to_wav(webm_path: str, wav_path: str):
    """
    Dùng ffmpeg để chuyển đổi từ định dạng .webm sang .wav
    """
    subprocess.run(["ffmpeg", "-y", "-i", webm_path, wav_path], check=True)

def speech_to_text(audio_bytes: bytes, language: str = "en") -> str:
    """
    Nhận bytes âm thanh (webm), chuyển sang wav rồi xử lý bằng Whisper.

    Tham số:
    - audio_bytes: dữ liệu âm thanh định dạng webm (dạng bytes)
    - language: mã ngôn ngữ để nhận dạng. Ví dụ:
        'en' - Tiếng Anh (mặc định)
        'vi' - Tiếng Việt
        'fr' - Tiếng Pháp
        'ru' - Tiếng Nga
        ...

    Trả về:
    - Chuỗi văn bản được chuyển từ âm thanh, hoặc chuỗi thông báo lỗi nếu thất bại.
    """
    try:
        # Bước 1: Lưu dữ liệu âm thanh dưới dạng file .webm tạm thời
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f_webm:
            f_webm.write(audio_bytes)
            f_webm.flush()
            webm_path = f_webm.name

        # Bước 2: Tạo đường dẫn cho file wav tạm thời
        wav_path = webm_path.replace(".webm", ".wav")

        # Bước 3: Dùng ffmpeg để chuyển từ .webm sang .wav
        convert_webm_to_wav(webm_path, wav_path)

        # Bước 4: Gọi Whisper để nhận dạng giọng nói, truyền ngôn ngữ được chọn
        # Nếu không truyền 'language', mặc định sẽ là 'en' (Tiếng Anh)
        result = model.transcribe(wav_path, language=language)

        # Bước 5: Xóa các file tạm sau khi xử lý xong
        os.remove(webm_path)
        os.remove(wav_path)

        return result["text"]

    except Exception as e:
        # Log lỗi nếu có sự cố trong quá trình chuyển đổi hoặc nhận dạng
        print(f"Lỗi chuyển âm thanh sang văn bản: {e}")
        return "[Lỗi chuyển âm thanh]"
