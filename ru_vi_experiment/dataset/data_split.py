import os
from sklearn.model_selection import train_test_split

# Đường dẫn đến tập dữ liệu
data_dir = os.path.expanduser("./train_data/OPUS-NeuLab-TedTalks/")
src_file = os.path.join(data_dir, "NeuLab-TedTalks.ru-vi.ru")
tgt_file = os.path.join(data_dir, "NeuLab-TedTalks.ru-vi.vi")

# Đọc dữ liệu
with open(src_file, 'r', encoding='utf-8') as f:
    src_lines = [line.strip() for line in f]

with open(tgt_file, 'r', encoding='utf-8') as f:
    tgt_lines = [line.strip() for line in f]

# Kiểm tra số dòng khớp
assert len(src_lines) == len(tgt_lines), "Số dòng không khớp giữa hai ngôn ngữ."

cleaned_data = [
    (src, tgt) for src, tgt in zip(src_lines, tgt_lines)
    if src.strip() and tgt.strip()
]

# Tách lại thành 2 danh sách
src_lines, tgt_lines = zip(*cleaned_data)

assert len(src_lines) == len(tgt_lines), "Số dòng không khớp giữa hai ngôn ngữ."

# Chia tập train/val/test
src_train, src_temp, tgt_train, tgt_temp = train_test_split(
    src_lines, tgt_lines, test_size=0.2, random_state=42)

src_val, src_test, tgt_val, tgt_test = train_test_split(
    src_temp, tgt_temp, test_size=0.9, random_state=42)

# Hàm ghi ra file
def write_file(path, lines):
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(line + '\n' for line in lines)

# Ghi file kết quả
output_dir = os.path.join(data_dir, "split")
os.makedirs(output_dir, exist_ok=True)

write_file(os.path.join(output_dir, "train.ru"), src_train)
write_file(os.path.join(output_dir, "train.vi"), tgt_train)

write_file(os.path.join(output_dir, "val.ru"), src_val)
write_file(os.path.join(output_dir, "val.vi"), tgt_val)

write_file(os.path.join(output_dir, "test.ru"), src_test)
write_file(os.path.join(output_dir, "test.vi"), tgt_test)

print("✅ Đã chia dữ liệu thành train/val/test và lưu tại:", output_dir)
