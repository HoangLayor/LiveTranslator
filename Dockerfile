# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements.txt từ thư mục gốc vào container
COPY requirements.txt .

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ thư mục backend vào container
COPY backend/ .

# Expose cổng mà app FastAPI sẽ chạy
EXPOSE 10000

# Chạy app bằng Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
