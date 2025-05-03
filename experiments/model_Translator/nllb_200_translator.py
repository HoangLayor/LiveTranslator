from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class NLLB200Translator:
  def __init__(self, model_name: str, device: str = None, direction: str = "ru2vi", max_length: int = 128, num_beams: int = 4):
    """
    Khởi tạo lớp dịch.
    - model_name: tên mô hình MarianMT (ví dụ: Helsinki-NLP/opus-mt-ru-vi)
    - device: 'cuda' hoặc 'cpu'
    - max_length: độ dài tối đa câu dịch
    - num_beams: số beam search cho decoding
    """
    self.model_name = model_name
    self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
    self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
    
    self.src_lang = "rus_Cyrl"   # Russian
    self.tgt_lang = "vie_Latn"   # Vietnamese

    if direction == "ru2vi":
      self.src_lang = "rus_Cyrl"
      self.tgt_lang = "vie_Latn"
    elif direction == "vi2ru":
      self.src_lang = "vie_Latn"
      self.tgt_lang = "rus_Cyrl"

    self.translator = pipeline("translation", model=self.model, tokenizer=self.tokenizer, src_lang=self.src_lang, tgt_lang=self.tgt_lang, max_length=400)

    self.max_length = max_length
    self.num_beams = num_beams

    self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    self.model = self.model.to(self.device)
    self.model.eval()

  def translate(self, sentence: str) -> str:
    """
    Dịch một câu từ ngôn ngữ nguồn sang ngôn ngữ đích.
    """
    output = self.translator(sentence)
    translated = output[0]["translation_text"]
    return translated
