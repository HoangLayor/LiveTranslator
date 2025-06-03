from googletrans import Translator
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# class OpusTranslator:
#   def __init__(self, model_name: str, device: str = None, max_length: int = 128, num_beams: int = 4):
#     """
#     Khởi tạo lớp dịch.
#     - model_name: tên mô hình MarianMT (ví dụ: Helsinki-NLP/opus-mt-ru-vi)
#     - device: 'cuda' hoặc 'cpu'
#     - max_length: độ dài tối đa câu dịch
#     - num_beams: số beam search cho decoding
#     """
#     self.model_name = model_name
#     self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, cache_dir="../../cache")
#     self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name, cache_dir="../../cache")
#     self.max_length = max_length
#     self.num_beams = num_beams

#     self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
#     self.model = self.model.to(self.device)
#     self.model.eval()

#   def translate(self, sentence: str) -> str:
#     """
#     Dịch một câu từ ngôn ngữ nguồn sang ngôn ngữ đích.
#     """
#     # Tokenize câu đầu vào
#     inputs = self.tokenizer(
#         sentence,
#         return_tensors="pt",
#         padding=True,
#         truncation=True,
#         max_length=self.max_length
#     ).to(self.device)

#     with torch.no_grad():
#         generated_ids = self.model.generate(
#           input_ids=inputs["input_ids"],
#           attention_mask=inputs["attention_mask"],
#           max_length=self.max_length,
#           num_beams=self.num_beams,
#           early_stopping=True
#         )

#     translated = self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)
#     return translated

# translator = {}
# translator["en_vi"] = OpusTranslator(model_name="Helsinki-NLP/opus-mt-en-vi")
# translator["vi_en"] = OpusTranslator(model_name="Helsinki-NLP/opus-mt-vi-en")
# translator["ru_vi"] = OpusTranslator(model_name="Helsinki-NLP/opus-mt-ru-vi")
# translator["vi_ru"] = OpusTranslator(model_name="Helsinki-NLP/opus-mt-vi-ru")

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
    'ru': 'Russian'
}

# def translate_text(text: str, source_lang: str = "auto", target_lang: str = "vi") -> str:
#     """
#     Dịch văn bản sử dụng googletrans
    
#     Args:
#         text: Văn bản cần dịch
#         target_lang: Ngôn ngữ đích (mặc định: tiếng Việt 'vi')
    
#     Returns:
#         Văn bản đã dịch hoặc thông báo lỗi nếu có
#     """
#     try:
#         if not text.strip():
#             return ""
#         # Phát hiện ngôn ngữ nguồn tự động
#         if source_lang == "auto":
#             translation = gg_translator.translate(text, dest=target_lang)
#             source_lang = translation.src
#             translation_text = translation.text
#         else:
#             translation_text = translator[source_lang + "_" + target_lang].translate(text)
#         return translation_text
        
#     except Exception as e:
#         return "[Lỗi dịch thuật]"
