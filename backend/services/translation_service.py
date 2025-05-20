from googletrans import Translator

# Khởi tạo Translator
translator = Translator(service_urls=[
    'translate.google.com',
    'translate.google.com.vn'
])

def translate_text(text: str, target_lang: str = "vi") -> str:
    """
    Dịch văn bản sử dụng googletrans
    
    Args:
        text: Văn bản cần dịch
        target_lang: Ngôn ngữ đích (mặc định: tiếng Việt 'vi')
    
    Returns:
        Văn bản đã dịch hoặc thông báo lỗi nếu có
    """
    try:
        if not text.strip():
            return ""
            
        # Phát hiện ngôn ngữ nguồn tự động
        translation = translator.translate(text, dest=target_lang)
        return translation.text
        
    except Exception as e:
        print(f"Lỗi khi dịch văn bản: {e}")
        return "[Lỗi dịch thuật]"

# Các ngôn ngữ hỗ trợ
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'vi': 'Tiếng Việt',
    'fr': 'French',
    'es': 'Spanish',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ru': 'Russian'
}