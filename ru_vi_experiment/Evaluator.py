import evaluate

class Evaluator:
  def __init__(self, metric_name="sacrebleu"):
    """
    Khởi tạo đối tượng Evaluator với tên metric.
    metric_name: str — tên của metric để đánh giá (mặc định là "sacrebleu").
    """
    self.metric = evaluate.load(metric_name)

  def compute(self, predictions, references):
    """
    predictions: List[str] — các câu mô hình đã dịch.
    references: List[str] — các câu tham chiếu (dịch đúng).
    """
    formatted_refs = [[ref] for ref in references]
    results = self.metric.compute(predictions=predictions, references=formatted_refs)
    return results
