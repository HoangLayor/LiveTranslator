from torch.utils.data import Dataset

class TransDataset(Dataset):
  def __init__(self, ru_file_path, vi_file_path, tokenizer, direction="ru2vi", max_length=512):
    """
    Dataset cho bài dịch tiếng Nga - tiếng Việt
    - source_file_path: Đường dẫn đến file nguồn
    - target_file_path: Đường dẫn đến file đích
    - tokenizer: Tokenizer sử dụng cho model
    - direction: Hướng dịch, có thể là "ru2vi" hoặc "vi2ru"
    - max_length: Độ dài tối đa của chuỗi đầu vào
    """
    self.direction = direction
    if self.direction not in ["ru2vi", "vi2ru"]:
      raise ValueError("direction phải là 'ru2vi' hoặc 'vi2ru'.")
    elif self.direction == "vi2ru":
      source_file_path = vi_file_path
      target_file_path = ru_file_path
    elif self.direction == "ru2vi":
      source_file_path = ru_file_path
      target_file_path = vi_file_path

    self.sources = self._read_file(source_file_path)
    self.targets = self._read_file(target_file_path)

    assert len(self.sources) == len(self.targets), "Số dòng không khớp !"

    self.tokenizer = tokenizer
    self.max_length = max_length
    

  def _read_file(self, file_path):
    """
    Đọc file và trả về danh sách các dòng
    """
    with open(file_path, "r", encoding="utf-8") as f:
      lines = [line.strip() for line in f.readlines()]
    return lines

  def __len__(self) -> int:
    """
    Trả về số lượng mẫu trong dataset
    """
    return len(self.sources)

  def __getitem__(self, idx) -> dict:
    """
    Trả về một mẫu dữ liệu
    """
    src_text = self.sources[idx]
    tgt_text = self.targets[idx]

    # Tokenize source
    inputs = self.tokenizer(
      src_text, return_tensors="pt", padding="max_length",
      truncation=True, max_length=self.max_length
    )

    # Tokenize target
    labels = self.tokenizer(
      tgt_text, return_tensors="pt", padding="max_length",
      truncation=True, max_length=self.max_length
    )

    return {
      "input_ids": inputs["input_ids"].squeeze(),
      "attention_mask": inputs["attention_mask"].squeeze(),
      "labels": labels["input_ids"].squeeze()
    }
