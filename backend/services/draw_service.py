import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import requests
from typing import List, Dict


class DrawService:
    def __init__(self, font_path: str = "arial.ttf", font_size: int = 16):
        self.font_path = font_path
        self.font_size = font_size

    def draw_text_on_image(self, image_url: str, text_regions: List[Dict]) -> bytes:
        response = requests.get(image_url)
        img_arr = np.asarray(bytearray(response.content), dtype=np.uint8)
        image = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)

        image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image_pil, "RGBA")
        font = ImageFont.truetype(self.font_path, self.font_size)

        for region in text_regions:
            x, y = region["x"], region["y"]
            w, h = region["width"], region["height"]
            translated = region.get("text", "")
            draw.rectangle([x, y, x + w, y + h], fill=(255,255,255,180))
            bbox = draw.textbbox((0, 0), translated, font=font)
            w_text = bbox[2] - bbox[0]
            h_text = bbox[3] - bbox[1]
            x_text = x + (w - w_text) // 2
            y_text = y + (h - h_text) // 2
            draw.text((x_text, y_text), translated, font=font, fill=(255,0,0,255))

        image_cv = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
        _, img_encoded = cv2.imencode('.jpg', image_cv)
        return img_encoded.tobytes()

        
            
