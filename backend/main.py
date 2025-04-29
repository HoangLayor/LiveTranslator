from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

# Khởi tạo FastAPI app và templates
app = FastAPI()

# Thêm middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hoặc danh sách các domain cụ thể bạn muốn cho phép
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép các phương thức HTTP như GET, POST, WebSocket
    allow_headers=["*"],  # Cho phép mọi headers
)

# Đặt đường dẫn cho thư mục tĩnh (css, js)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Đặt đường dẫn cho các templates (HTML)
templates = Jinja2Templates(directory="frontend/templates")

# Route cho trang chủ
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
