# 🌐 LiveTranslator - Hệ thống dịch ngôn ngữ theo thời gian thực

## Giới thiệu
**RealTime-Translator** là một hệ thống dịch ngôn ngữ theo thời gian thực từ giọng nói người dùng. Dự án bao gồm backend được xây dựng bằng FastAPI, hỗ trợ các API RESTful và WebSocket để xử lý dữ liệu audio, chuyển giọng nói thành văn bản (Speech-to-Text), dịch sang ngôn ngữ khác (Translation), và chuyển văn bản thành giọng nói (Text-to-Speech).

Hệ thống được thiết kế linh hoạt để tích hợp nhiều mô hình hoặc API khác nhau như Whisper, Google Cloud Speech, MarianMT, OpenAI, gTTS, v.v. Phần giao diện frontend sử dụng HTML/CSS/JS và WebSocket để tương tác thời gian thực với người dùng.

---

## Tính năng

### Chức năng chính
- 🎙️ **Nhận dạng giọng nói (STT)**: Nhận audio đầu vào, chuyển thành văn bản.
- 🌍 **Dịch ngôn ngữ (Translation)**: Dịch văn bản sang ngôn ngữ đích.
- 🔊 **Tổng hợp giọng nói (TTS)**: Chuyển văn bản dịch thành âm thanh phát lại.
- ⚡ **WebSocket**: Giao tiếp real-time giữa frontend và backend.
- 📁 **API RESTful**: Hỗ trợ các request thông thường cho STT, dịch và TTS.
- 🖥️ **Giao diện web**: Giao diện thân thiện, hỗ trợ nhập liệu bằng giọng nói và văn bản.

### Chức năng mở rộng
- 🧩 **Tùy chọn mô hình/API**: Cho phép chọn công cụ STT/Translation/TTS phù hợp.
- 💾 **Lưu lịch sử phiên dịch** *(tuỳ chọn)*
- 👥 **Xử lý nhiều người dùng đồng thời** *(qua WebSocket room ID)*

---

## Cấu trúc dự án
```
LiveTranslator/
├── backend/
│   ├── api/                              # Các route API & WebSocket
│   │   ├── rest_routes.py                # Các route REST (các endpoint API chính)
│   │   └── ws_routes.py                  # WebSocket route (xử lý kết nối WebSocket)
│   ├── services/                         # Logic chính: STT, Translation, TTS, WebSocket
│   │   ├── stt_service.py                # Xử lý nhận diện giọng nói (STT)
│   │   ├── translation_service.py        # Xử lý dịch ngôn ngữ (Translation)
│   │   ├── tts_service.py                # Xử lý tạo giọng nói (TTS)
│   │   └── websocket_service.py          # Xử lý WebSocket communication
│   ├── models/                           # Schema dữ liệu (Pydantic models)
│   │   ├── stt_model.py                  # Model cho dữ liệu STT
│   │   ├── translation_model.py          # Model cho dữ liệu Translation
│   │   └── tts_model.py                  # Model cho dữ liệu TTS
│   ├── utils/                            # Hàm tiện ích và các công cụ hỗ trợ khác
│   │   ├── audio_utils.py                # Xử lý file âm thanh
│   │   └── error_handler.py              # Xử lý lỗi trong hệ thống
│   ├── test/                             # Thư mục kiểm thử (unit tests và integration tests)
│   │   ├── test_stt_service.py           # Kiểm thử các hàm trong stt_service.py
│   │   ├── test_translation_service.py   # Kiểm thử các hàm trong translation_service.py
│   │   ├── test_tts_service.py           # Kiểm thử các hàm trong tts_service.py
│   │   └── test_websocket_service.py     # Kiểm thử các hàm trong websocket_service.py
│   ├── main.py                           # Entry point FastAPI app (ứng dụng FastAPI chính)
│   └── requirements.txt                  # Thư viện cần thiết (dependencies)
├── frontend/                             # Giao diện người dùng (React frontend)
│   ├── templates/                        # HTML templates
│   │   └── index.html                    # Trang chính của frontend (React app)
│   └── static/                           # Các file tĩnh: CSS, JS
│       ├── css/    
│       │   └── style.css                 # File CSS chính của frontend
│       └── js/    
│           └── ws-client.js              # JS để gửi và nhận dữ liệu qua WebSocket
├── docs/                                 # Tài liệu hướng dẫn
│   ├── api.md                            # Tài liệu mô tả các API của backend
│   ├── setup.md                          # Hướng dẫn cài đặt môi trường phát triển
│   └── deploy.md                         # Hướng dẫn triển khai ứng dụng lên server
├── scripts/                              # Các script setup/dev
│   ├── setup.sh                          # Cài đặt môi trường phát triển
│   └── dev.sh                            # Script để chạy các dịch vụ trong môi trường dev
├── Dockerfile                            # Cấu hình Docker build cho dự án
├── docker-compose.yml                    # Cấu hình Docker Compose để chạy toàn bộ hệ thống
├── .env.example                          # Mẫu file cấu hình môi trường
├── .gitignore                            # Các file và thư mục không được theo dõi trong git
└── README.md                             # Tài liệu mô tả dự án, cách sử dụng và cài đặt

```

---

## Yêu cầu kỹ thuật
- **Ngôn ngữ backend**: Python 3.9+
- **Framework**: FastAPI
- **Thư viện chính**:
  - `uvicorn`, `fastapi`, `pydantic`
  - `websockets`, `python-multipart`, `httpx`
  - Tuỳ chọn theo từng dịch vụ: `openai`, `transformers`, `gtts`, `whisper`
- **Frontend**: HTML/CSS/JS/REACT + WebSocket + Jinja2 (cho templating trong Flask/FastAPI)
- **Docker (tuỳ chọn)**: Triển khai dễ dàng

---

## Hướng dẫn cài đặt và chạy dự án

### 1. Clone repository
```bash
git clone https://github.com/yourname/LiveTranslator.git
cd LiveTranslator
```

### 2. Tạo môi trường ảo & cài đặt
```bash
python -m venv venv
source venv/bin/activate  # hoặc .\venv\Scripts\activate trên Windows
pip install -r backend/requirements.txt
```

### 3. Cấu hình môi trường
```bash
cp .env.example .env  # hoặc tự tạo file .env
```

### 4. Chạy backend server
```bash
uvicorn backend.main:app --reload
```
- Truy cập tại: `http://localhost:8000`

### 5. (Tùy chọn) Chạy với Docker
```bash
docker-compose up --build
```

---

## API Endpoints

### REST API
- `POST /stt`: Nhận file âm thanh, trả về văn bản
- `POST /translate`: Dịch văn bản sang ngôn ngữ đích
- `POST /tts`: Chuyển văn bản thành audio (base64)

### WebSocket
- `ws://localhost:8000/ws/audio`
  - Gửi audio chunk dạng `bytes`
  - Nhận văn bản dịch dạng `text`

---

## Hướng dẫn đóng góp

1. Fork và clone repo
2. Tạo branch mới
3. Commit theo chuẩn message rõ ràng
4. Tạo Pull Request với mô tả thay đổi

> Quy tắc: code rõ ràng, đặt tên chuẩn, ưu tiên modular hoá và viết docstring.

---

## Xử lý lỗi
- ❌ Kiểm tra audio không đúng định dạng
- ❌ WebSocket mất kết nối
- ❌ Mô hình API trả về lỗi
- ✅ Sử dụng `try-except` và `HTTPException` trong FastAPI
- ✅ Log lỗi chi tiết tại backend và phản hồi rõ ràng tới frontend

---

> RealTime-Translator được thiết kế để mở rộng và tích hợp với nhiều hệ thống nhận dạng/ngôn ngữ khác nhau. Chúng tôi chào đón mọi đóng góp và phản hồi từ cộng đồng! 🚀

