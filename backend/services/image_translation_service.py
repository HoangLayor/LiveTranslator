import requests
import json
import base64
from typing import List, Dict, Any
import os
import base64
import imghdr
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from datetime import datetime
import cloudinary
import cloudinary.uploader
import google.generativeai as genai

# Load environment variables
load_dotenv()

class ImageTranslationService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        # self.headers = {
        #     "Authorization": f"Bearer {api_key}",
        #     "Content-Type": "application/json",
        #     "HTTP-Referer": os.getenv("SITE_URL", "http://localhost:8000"),
        #     "X-Title": os.getenv("SITE_NAME", "LiveTranslator")
        # }

        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.model_name = "gemini-2.5-flash-preview-05-20"
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def encode_image(self, image_input):
        if isinstance(image_input, str):
            # Case 1: Input is file path
            with open(image_input, "rb") as f:
                image_bytes = f.read()
            ext = imghdr.what(None, h=image_bytes)
            media_type = f"image/{ext or 'jpeg'}"

        elif isinstance(image_input, Image.Image):
            # Case 2: Input is a Pillow Image
            buffer = BytesIO()
            image_input.save(buffer, format="PNG")  # default to PNG
            image_bytes = buffer.getvalue()
            media_type = "image/png"

        elif isinstance(image_input, (bytes, BytesIO)):
            # Case 3: Raw bytes or file-like object
            if isinstance(image_input, BytesIO):
                image_bytes = image_input.getvalue()
            else:
                image_bytes = image_input
            ext = imghdr.what(None, h=image_bytes)
            media_type = f"image/{ext or 'jpeg'}"

        else:
            raise TypeError("Unsupported image input type")

        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        return base64_image, media_type

    # def encode_image(self, image_path: str) -> str:
    #     """Convert image to base64 string"""
    #     with open(image_path, "rb") as image_file:
    #         return base64.b64encode(image_file.read()).decode('utf-8')

    def upload_image_to_cloudinary(self, image_bytes: bytes) -> str:
        """
        Upload image to Cloudinary using unsigned upload (no API key required).
        Args:
            image_bytes: Image data in bytes
        Returns:
            str: Public URL of the uploaded image
        """
        try:
            cloud_name = "dpqs4s1xm"  
            upload_preset = "unsigned_demo" 

            url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
            files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
            data = {'upload_preset': upload_preset}

            response = requests.post(url, files=files, data=data)
            response.raise_for_status()

            upload_result = response.json()
            return upload_result.get("secure_url")
        
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return None

    def extract_sentences_with_positions(self, image_url: str) -> List[Dict[str, Any]]:
        """
        Extract text and positions from image using OpenRouter API
        Args:
            image_url: URL of the image
        Returns:
            List of dictionaries containing text and positions
        """
        try:
            # Prepare the request payload
            payload = {
                "model": "google/gemini-2.5-flash-preview-05-20",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """
                                Hãy phân tích ảnh này và trích xuất tất cả đoạn text. 
                                Với mỗi đoạn, trả về:
                                - text gốc
                                - x, y, width, height (tọa độ pixel tuyệt đối trên ảnh gốc, với (0,0) là góc trên bên trái, đơn vị là pixel)
                                Format kết quả là JSON array như sau:
                                [
                                  {
                                    "type": "translation-image",
                                    "text": "nội dung text",
                                    "x": 123,
                                    "y": 45,
                                    "width": 67,
                                    "height": 20
                                  }
                                ]
                                """
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ]
            }

            # Make the API request
            response = requests.post(
                url=f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            
            # Check for errors
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Extract JSON from the response text
            json_str = content[content.find('['):content.rfind(']')+1]
            return json.loads(json_str)
            
        except Exception as e:
            print(f"Error extracting text: {e}")
            return []
        
    def extract_sentences_with_positions_by_gemini(self, image) -> List[Dict[str, Any]]:
        base64_image, media_type = self.encode_image(image)
        prompt = """
        Bạn là một chuyên gia phân tích thị giác ngôn ngữ AI với năng lực OCR tiên tiến, được tinh chỉnh để trích xuất văn bản từ hình ảnh một cách chính xác và hiệu quả. Nhiệm vụ của bạn là phân tích sâu sắc và kỹ lưỡng mọi pixel trong hình ảnh được cung cấp, bất kể đó là tài liệu quét, ảnh chụp màn hình, ảnh chụp văn bản in, hay bất kỳ dạng tài liệu trực quan nào khác.
        - Mục tiêu cốt lõi là phát hiện và trích xuất tất cả các đoạn văn bản có ý nghĩa, dễ đọc và hoàn chỉnh (có thể là một từ, một câu, hoặc một đoạn văn đầy đủ).
        - Đối với mỗi đoạn văn bản được trích xuất, bạn phải cung cấp thông tin chi tiết dưới dạng đối tượng JSON theo cấu trúc sau:
        {
        "type": "extracted-text-segment",
        "text": "văn bản được trích xuất nguyên bản",
        "x": ..., // Tọa độ X của góc trên bên trái của vùng văn bản (pixel tuyệt đối)
        "y": ..., // Tọa độ Y của góc trên bên trái của vùng văn bản (pixel tuyệt đối)
        "width": ..., // Chiều rộng của vùng văn bản (pixel tuyệt đối)
        "height": ... // Chiều cao của vùng văn bản (pixel tuyệt đối)
        }
        Các quy tắc và yêu cầu bắt buộc để đảm bảo chất lượng cao nhất:
        - Định dạng đầu ra: Toàn bộ kết quả phải được trả về dưới dạng một mảng JSON (JSON Array) chứa các đối tượng JSON đã định dạng ở trên.
        - Hệ tọa độ ảnh: Gốc tọa độ (0,0) được đặt ở góc trên bên trái của hình ảnh. Tất cả các giá trị tọa độ và kích thước phải là pixel tuyệt đối (absolute pixels).
        - Độ bao phủ toàn diện: Đảm bảo mọi đoạn văn bản có thể đọc được trong hình ảnh đều được trích xuất. Không bỏ sót bất kỳ phần văn bản nào, kể cả các chú thích nhỏ, số trang, hoặc tiêu đề.
        - Tính toàn vẹn và ngữ nghĩa của văn bản:Hãy ưu tiên gom các từ và dòng có liên quan về mặt ngữ nghĩa và vị trí thành các đoạn văn bản hoàn chỉnh và có nghĩa. Ví dụ: một câu dài trải qua nhiều dòng nên được trích xuất thành một text duy nhất.
        - Phân biệt và trích xuất riêng biệt các khối văn bản rõ ràng, ví dụ: tiêu đề, đoạn văn chính, danh sách, chú thích.
        Bảo toàn nguyên bản và định dạng:Không tự ý dịch, tóm tắt, hay chỉnh sửa nội dung văn bản. Trả về văn bản chính xác như những gì hiển thị trong hình ảnh.
        - Giữ nguyên chữ hoa, chữ thường, dấu câu, ký tự đặc biệt, và các định dạng hiển thị (ví dụ: in đậm, in nghiêng, gạch chân). Đặc biệt chú ý đến các tiêu đề, tên riêng, hoặc các phần văn bản được nhấn mạnh.
        - Xử lý thách thức thị giác:Đặc biệt chú ý đến các văn bản có độ tương phản thấp, phông chữ khác lạ, hoặc bị mờ nhẹ. Cố gắng tối đa để trích xuất ngay cả trong điều kiện khó khăn.
        - Nếu có văn bản bị xoay hoặc nằm trên nền phức tạp, hãy cố gắng điều chỉnh để trích xuất chính xác.
        Ví dụ về cấu trúc đầu ra mong muốn:
        [
        {
            "type": "extracted-text-segment",
            "text": "Đoạn văn bản chính đầu tiên, có thể trải dài qua nhiều dòng và thể hiện nội dung quan trọng.",
            "x": 80,
            "y": 45,
            "width": 500,
            "height": 70
        },
        {
            "type": "extracted-text-segment",
            "text": "TIÊU ĐỀ IN ĐẬM VÀ CÓ VỊ TRÍ NỔI BẬT",
            "x": 150,
            "y": 130,
            "width": 350,
            "height": 40
        },
        {
            "type": "extracted-text-segment",
            "text": "Chân trang - Trang 1/5",
            "x": 600,
            "y": 750,
            "width": 120,
            "height": 15
        }
        ]
        """
        response = self.model.generate_content([
            {
                'mime_type':media_type, 
                'data': base64_image
            }, 
            prompt,
        ])

        content = response.text
        json_str = content[content.find('['):content.rfind(']')+1]
        return json.loads(json_str)
