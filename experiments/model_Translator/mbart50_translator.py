from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class MBART50Translator:
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

    self.ru_lang = "ru_RU"   # Russian
    self.vi_lang = "vi_VN"   # Vietnamese

    if direction == "ru2vi":
        self.src_lang = self.ru_lang
        self.tgt_lang = self.vi_lang
    elif direction == "vi2ru":
        self.src_lang = self.vi_lang
        self.tgt_lang = self.ru_lang

    # self.translator = pipeline("translation", model=self.model, tokenizer=self.tokenizer, src_lang=self.src_lang, tgt_lang=self.tgt_lang, max_length=400)
    self.tokenizer.src_lang = self.src_lang

    self.max_length = max_length
    self.num_beams = num_beams

    self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    self.model = self.model.to(self.device)
    self.model.eval()

  def translate(self, sentence: str) -> str:
    """
    Dịch một câu từ ngôn ngữ nguồn sang ngôn ngữ đích.
    """
    # output = self.translator(sentence)
    # translated = output[0]["translation_text"]

    input_ids = self.tokenizer(sentence, return_tensors="pt").to(self.device)
    generated_tokens = self.model.generate(
        **input_ids,
        forced_bos_token_id=self.tokenizer.lang_code_to_id[self.tgt_lang],
        max_length=self.max_length,
        num_beams=self.num_beams,
    )
    translated = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
    return translated