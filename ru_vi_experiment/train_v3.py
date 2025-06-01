import os
import time
from tqdm import tqdm
import json
import torch
import pandas as pd
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from torch.optim import AdamW

from Translators import OpusTranslator
from MyDataset import TransDataset
from Evaluator import Evaluator

log_dir = "runs/ru_vi_experiment"
save_dir = os.path.join(log_dir, time.strftime("%Y-%m-%d_%H-%M-%S"))

if not os.path.exists(save_dir):
    os.makedirs(save_dir)

writer = SummaryWriter(log_dir=save_dir)
evaluator = Evaluator()

num_epochs = 3
batch_size = 16
learning_rate = 5e-5
max_length = 128

data_dir = "./dataset/train_data/OPUS-NeuLab-TedTalks/split"
train_ru_path = f"{data_dir}/train.ru"
train_vi_path = f"{data_dir}/train.vi"
test_ru_path  = f"{data_dir}/val.ru"
test_vi_path  = f"{data_dir}/val.vi"

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


def evaluate_all(translator, dataloader, max_length=128, device='cuda'):
    existing_files = [f for f in os.listdir(save_dir) if f.startswith("predictions")]
    if existing_files:
        existing_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
        next_index = int(existing_files[-1].split('_')[1].split('.')[0]) + 1
    else:
        next_index = 1
    save_path = os.path.join(save_dir, f"predictions_{next_index}.csv")

    
    translator.model.eval()
    predictions = []

    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating"):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)

            outputs = translator.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_length=max_length,
                num_beams=translator.num_beams,
                early_stopping=True
            )

            # Decode từng dòng trong output
            preds = translator.tokenizer.batch_decode(outputs, skip_special_tokens=True)
            predictions.extend(preds)

    df = pd.DataFrame({
        "prediction": predictions
    })
    df.to_csv(save_path, index=False)
    print(f"Predictions saved to {save_path}")

    translator.model.train()
    return predictions

print(len(train_dataset))
print(len(test_dataset))

results = evaluate_all(translator, test_dataloader)
bleu_score = results
print(f"BLEU Score before fine-tuning: {bleu_score}")

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

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        pbar.set_postfix(loss=loss.item())

    writer.add_scalar("Loss/train", loss.item(), epoch * len(train_dataloader) + 1)
    print(f"✅ Epoch {epoch+1} completed. Avg Loss: {total_loss / len(train_dataloader):.4f}")

    # Đánh giá mô hình sau mỗi epoch
    results = evaluate_all(translator, test_dataloader)
    bleu_score = results
    print(f"BLEU Score: {bleu_score}")


# Lưu mô hình fine-tuned
translator.model.save_pretrained("./ru-vi-finetuned/last_model")
tokenizer.save_pretrained("./ru-vi-finetuned/last_model")