# punctuation.py
import re
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

# 1. Chỉ tải mô hình và tokenizer một lần (khi import file này)
#    - Nếu bạn có GPU, set device=0; nếu không có GPU, device=-1 sẽ dùng CPU
DEVICE = 0 if torch.cuda.is_available() else -1

punct_model = AutoModelForTokenClassification.from_pretrained(
    "oliverguhr/fullstop-punctuation-multilang-large"
)
punct_tokenizer = AutoTokenizer.from_pretrained(
    "oliverguhr/fullstop-punctuation-multilang-large"
)
punct_pipeline = pipeline(
    task="ner",
    model=punct_model,
    tokenizer=punct_tokenizer,
    aggregation_strategy="simple",
    device=DEVICE,        # <-- nếu có GPU, pipeline sẽ chạy trên GPU
)

# 2. Hàm viết hoa sau dấu câu (unchanged)
def capitalize_after_punctuation(text: str) -> str:
    text = text.strip()
    if not text:
        return text

    # Viết hoa chữ cái đầu tiên trong chuỗi
    text = text[0].upper() + text[1:]

    # Viết hoa chữ cái đầu sau dấu . ? !
    def repl(match):
        return match.group(1) + match.group(2).upper()

    pattern = r'([.?!]\s+)(\w)'
    text = re.sub(pattern, repl, text)
    return text

# 3. Hàm phục hồi dấu câu
def restore_punctuation(text: str) -> str:
    """
    Trả về chuỗi đã gán dấu câu và viết hoa thích hợp, hỗ trợ đầy đủ các loại dấu câu.
    """
    with torch.no_grad():
        tokens = text.strip().split()
        predictions = punct_pipeline(" ".join(tokens))

    result = []
    for pred in predictions:
        word = pred["word"]
        entity = pred["entity_group"]

        # Viết hoa
        if entity == "CAP":
            word = word.capitalize()
        # Dấu câu được mô hình hỗ trợ
        elif entity in {".", ",", "?", "!", ":", ";"}:
            word = word + entity + " "

        result.append(word)

    # Ghép lại và xóa khoảng trắng dư
    return " ".join(result).strip()

