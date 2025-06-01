from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class OpusTranslator:
  def __init__(self, model_name: str, device: str = None, max_length: int = 128, num_beams: int = 4):
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
    self.max_length = max_length
    self.num_beams = num_beams

    self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    self.model = self.model.to(self.device)
    self.model.eval()

  def translate(self, sentence: str) -> str:
    """
    Dịch một câu từ ngôn ngữ nguồn sang ngôn ngữ đích.
    """
    # Tokenize câu đầu vào
    inputs = self.tokenizer(
        sentence,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=self.max_length
    ).to(self.device)

    with torch.no_grad():
        generated_ids = self.model.generate(
          input_ids=inputs["input_ids"],
          attention_mask=inputs["attention_mask"],
          max_length=self.max_length,
          num_beams=self.num_beams,
          early_stopping=True
        )

    translated = self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)
    return translated

if __name__ == "__main__":
    # Ví dụ sử dụng
    translator = OpusTranslator("Helsinki-NLP/opus-mt-ru-vi")
    sentence = "Привет, как дела?"
    translated_sentence = translator.translate(sentence)
    print(f"Câu gốc: {sentence}")
    print(f"Câu dịch: {translated_sentence}")