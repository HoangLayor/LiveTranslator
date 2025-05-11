import os
import time
from tqdm import tqdm
import json
import torch
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from transformers import AdamW, get_scheduler

from Translators import OpusTranslator
from MyDataset import TransDataset
from Evaluator import Evaluator
from accelerate import Accelerator

# Khởi tạo Accelerator
accelerator = Accelerator()

writer = SummaryWriter(log_dir="runs/ru_vi_experiment")
evaluator = Evaluator()

num_epochs = 3
batch_size = 8
learning_rate = 5e-5
max_length = 128

train_data_dir = "./dataset/train_data/OPUS-MultiCCAligned"
test_data_dir = "./dataset/test_data/OPUS-Tatoeba"
train_ru_path = f"{train_data_dir}/MultiCCAligned.ru-vi.ru"
train_vi_path = f"{train_data_dir}/MultiCCAligned.ru-vi.vi"
test_ru_path  = f"{test_data_dir}/Tatoeba.ru-vi.ru"
test_vi_path  = f"{test_data_dir}/Tatoeba.ru-vi.vi"

device = "cuda" if torch.cuda.is_available() else "cpu"
model_name = "Helsinki-NLP/opus-mt-ru-vi"
# model_name = "Helsinki-NLP/opus-mt-vi-ru"

if "ru-vi" in model_name:
    direction = "ru2vi"
elif "vi-ru" in model_name:
    direction = "vi2ru"

translator = OpusTranslator(model_name, device=device, max_length=max_length, num_beams=4)
tokenizer = translator.tokenizer

train_dataset = TransDataset(train_ru_path, train_vi_path, tokenizer, direction=direction)
test_dataset = TransDataset(test_ru_path, test_vi_path, tokenizer, direction=direction)

train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_dataloader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

# Optimizer
optimizer = AdamW(translator.model.parameters(), lr=learning_rate)
num_training_steps = len(train_dataloader) * 10
lr_scheduler = get_scheduler("linear", optimizer=optimizer, num_warmup_steps=0, num_training_steps=num_training_steps)

# Accelerate
accelerator = Accelerator()
translator, optimizer, train_dataloader, test_dataloader, lr_scheduler = accelerator.prepare(
    translator, optimizer, train_dataloader, test_dataloader, lr_scheduler
)

def evaluate_model(translator, sources, targets):
    translator.model.eval()
    predictions = []
    with torch.no_grad():
        for source in tqdm(sources, desc="Evaluating"):
            translated = translator.translate(source)
            predictions.append(translated)

    translator.model.train()
    # Đánh giá mô hình
    results = evaluator.compute(predictions, targets)
    return results

# Đánh giá mô hình trước khi fine-tune
results = evaluate_model(translator, test_dataset.sources, test_dataset.targets)
bleu_score = results["score"]
print(f"BLEU Score before fine-tuning: {bleu_score:.2f}")

# Training Loop
translator.model.train()
for epoch in range(num_epochs):
    total_loss = 0
    pbar = tqdm(train_dataloader, desc=f"Epoch {epoch+1}")

    for batch in pbar:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        outputs = translator.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )

        loss = outputs.loss
        total_loss += loss.item()

        accelerator.backward(loss)
        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()

        pbar.set_postfix(loss=loss.item())

    writer.add_scalar("Loss/train", loss.item(), epoch * len(train_dataloader) + 1)
    print(f"✅ Epoch {epoch+1} completed. Avg Loss: {total_loss / len(train_dataloader):.4f}")

    # Đánh giá mô hình sau mỗi epoch
    results = evaluate_model(translator.model, test_dataset.sources, test_dataset.targets)
    bleu_score = results["score"]
    print(f"BLEU Score: {bleu_score:.2f}")


# Lưu mô hình fine-tuned
accelerator.wait_for_everyone()
unwrapped = accelerator.unwrap_model(translator.model)
unwrapped.save_pretrained("./ru_vi_finetuned/best_model", save_function=accelerator.save)
tokenizer.save_pretrained("./ru_vi_finetuned/best_model")