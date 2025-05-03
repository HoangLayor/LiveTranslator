from transformers import MT5ForConditionalGeneration, MT5Tokenizer
import torch

class MT5Translator:
  def __init__(self, model_name: str, device: str = None, direction: str = "ru2vi", max_length: int = 128, num_beams: int = 4):
    """
    Khởi tạo lớp dịch.
    - model_name: tên mô hình
    - device: 'cuda' hoặc 'cpu'
    - max_length: độ dài tối đa câu dịch
    - num_beams: số beam search cho decoding
    """
    self.model_name = model_name
    self.model = MT5ForConditionalGeneration.from_pretrained(self.model_name)
    self.tokenizer = MT5Tokenizer.from_pretrained(self.model_name)

    self.max_length = max_length
    self.num_beams = num_beams
    self.direction = direction
    if self.direction == "ru2vi":
        self.prompt = f"Translate Russian to Vietnamese:"
    elif self.direction == "vi2ru":
        self.prompt = f"Translate Vietnamese to Russian:"
    else:
        raise ValueError("Invalid translation direction. Use 'ru2vi' or 'vi2ru'.")

    self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    self.model = self.model.to(self.device)
    self.model.eval()

  def translate(self, sentence: str) -> str:
    """
    Dịch một câu từ ngôn ngữ nguồn sang ngôn ngữ đích.
    """
    input_ids = self.tokenizer(
        f"{self.prompt} {sentence}", return_tensors="pt"
    ).input_ids.to(self.device)  # Batch size 1
    outputs = self.model.generate(input_ids)
    translated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
    return translated

if __name__ == "__main__":
    model_name = "google/mt5-base"
    translator = MT5Translator(model_name=model_name, direction="ru2vi")
    sentence = "Мне пора идти спать."
    translated = translator.translate(sentence)
    print(f"Translated: {translated}")