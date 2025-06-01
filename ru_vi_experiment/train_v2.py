from datasets import load_dataset
import evaluate
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, DataCollatorForSeq2Seq, Seq2SeqTrainer, Seq2SeqTrainingArguments
from MyDataset import TransDataset

bleu = evaluate.load("sacrebleu")

def compute_metrics(eval_preds):
    preds, labels = eval_preds
    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

    # sacreBLEU expects list of list of references
    decoded_labels = [[label] for label in decoded_labels]
    result = bleu.compute(predictions=decoded_preds, references=decoded_labels)
    return {"bleu": result["score"]}

# Load tokenizer và model
model_name = "Helsinki-NLP/opus-mt-ru-vi"
# model_name = "Helsinki-NLP/opus-mt-vi-ru"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

if "ru-vi" in model_name:
    direction = "ru2vi"
elif "vi-ru" in model_name:
    direction = "vi2ru"

train_data_dir = "./dataset"
test_data_dir = "./test_data/OPUS-Tatoeba"
train_ru_path = f"{train_data_dir}/OpenSubtitles.ru-vi.ru"
train_vi_path = f"{train_data_dir}/OpenSubtitles.ru-vi.vi"
test_ru_path  = f"{test_data_dir}/Tatoeba.ru-vi.ru"
test_vi_path  = f"{test_data_dir}/Tatoeba.ru-vi.vi"

train_dataset = TransDataset(train_ru_path, train_vi_path, tokenizer, direction=direction)
val_dataset = TransDataset(test_ru_path, test_vi_path, tokenizer, direction=direction)
print("Train dataset size:", len(train_dataset))
print("Validation dataset size:", len(val_dataset))

# Training arguments
training_args = Seq2SeqTrainingArguments(
    output_dir="./ru-vi-finetuned",
    per_device_train_batch_size=16,
    learning_rate=5e-5,
    num_train_epochs=3,
    logging_dir="./train_logs",
    save_total_limit=2,
    save_steps=500,
    eval_strategy="epoch",  # hoặc "steps"
    eval_steps=500,               # nếu dùng evaluation_strategy="steps"
    save_strategy="epoch",        # để lưu sau mỗi epoch
    fp16=True,
    load_best_model_at_end=True,  # cần thiết cho early stopping
    metric_for_best_model="bleu", # hoặc "loss"
    greater_is_better=True        # BLEU càng cao càng tốt
)

# Trainer
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    processing_class=tokenizer,
    compute_metrics=compute_metrics
)


# Train
print("Start training...")
trainer.train()

# Save model
trainer.save_model("./ru-vi-finetuned")
