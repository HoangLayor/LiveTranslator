import requests
import json
import base64
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from datetime import datetime
import cloudinary
import cloudinary.uploader
from backend.services.translation_service import translate_text

# Load environment variables
load_dotenv()

class ImageTranslationService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv("SITE_URL", "http://localhost:8000"),
            "X-Title": os.getenv("SITE_NAME", "LiveTranslator")
        }

    def encode_image(self, image_path: str) -> str:
        """Convert image to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def upload_image_to_cloudinary(self, image_bytes: bytes, api_key: str) -> str:
        """
        Upload image to Cloudinary and return the URL
        Args:
            image_bytes: Image data in bytes
            api_key: Cloudinary API key
        Returns:
            str: Public URL of the uploaded image
        """
        try:
            # Configure Cloudinary
            cloudinary.config(
                cloud_name="dw9bbrnke",
                api_key="639987295942778",
                api_secret="g9AIU2wXL2JtYavmHKukq0SgNTg"
            )
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"translation_{timestamp}"
            
            # Upload image
            result = cloudinary.uploader.upload(
                image_bytes,
                public_id=filename,
                resource_type="image",
                overwrite=True
            )
            
            # Return secure URL
            return result.get('secure_url')
            
        except Exception as e:
            print(f"Error uploading to Cloudinary: {e}")
            raise Exception(f"Failed to upload image: {str(e)}")

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
