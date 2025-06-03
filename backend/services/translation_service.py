from googletrans import Translator

# Khởi tạo Translator
translator = Translator(service_urls=[
    'translate.google.com',
    'translate.google.com.vn'
])

def translate_text(text: str, source_lang: str = "auto", target_lang: str = "vi") -> str:
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
        if source_lang == "auto":
            translation = translator.translate(text, dest=target_lang)
            source_lang = translation.src
        else:
            translation = translator.translate(text, src=source_lang, dest=target_lang)
        return translation.text
        
    except Exception as e:
        return "[Lỗi dịch thuật]"

# Các ngôn ngữ hỗ trợ
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'vi': 'Tiếng Việt',
    'fr': 'French',
    'ru': 'Russian',
    'zh-cn': 'Chinese (Simplified)'
}