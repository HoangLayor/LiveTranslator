from transformers import AutoTokenizer, MarianMTModel
from googletrans import Translator
from backend.utils.logger import setup_logger

logger = setup_logger()

# Khởi tạo Translator
gg_translator = Translator(service_urls=[
    'translate.google.com',
    'translate.google.com.vn'
])

# Các ngôn ngữ hỗ trợ
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'fr': 'French',
    'ru': 'Russian',
    # 'zh': 'Chinese (Simplified)'
}

translator = {}

def load_models():
    global translator
    cache_dir = "../cache"
    # Tải các mô hình dịch thuật từ Hugging Face
    for lang in SUPPORTED_LANGUAGES.keys():
        logger.info(f"Loading translation model for {lang}_vi")
        translator[f"{lang}_vi"] = {
            'model': MarianMTModel.from_pretrained(f"Helsinki-NLP/opus-mt-{lang}-vi", cache_dir=cache_dir),
            'tokenizer': AutoTokenizer.from_pretrained(f"Helsinki-NLP/opus-mt-{lang}-vi", cache_dir=cache_dir)
        }
        if lang == 'zh':
            continue
        logger.info(f"Loading translation model for vi_{lang}")
        translator[f"vi_{lang}"] = {
            'model': MarianMTModel.from_pretrained(f"Helsinki-NLP/opus-mt-vi-{lang}", cache_dir=cache_dir),
            'tokenizer': AutoTokenizer.from_pretrained(f"Helsinki-NLP/opus-mt-vi-{lang}", cache_dir=cache_dir)
        }

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
            translation = gg_translator.translate(text, dest=target_lang)
            source_lang = translation.src
            logger.info(f"Using gg translator for auto detection: {source_lang} to {target_lang}")
        elif source_lang != "vi" or target_lang != "vi":
            translation = gg_translator.translate(text, src=source_lang, dest=target_lang)
            logger.info(f"Using gg translator for {source_lang} to {target_lang}")
        else:
            logger.info("Using Hugging Face model for translation")
            tokenizer = translator[f"{source_lang}_{target_lang}"]['tokenizer']
            model = translator[f"{source_lang}_{target_lang}"]['model']
            # Tokenize the input text
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            translated = model.generate(**inputs)
            translation_text = tokenizer.decode(translated[0], skip_special_tokens=True)
            return translation_text
        
        return translation.text
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return "[Lỗi dịch thuật]"

