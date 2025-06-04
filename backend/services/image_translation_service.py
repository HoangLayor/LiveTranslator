import requests
import json
import base64


class ImageTranslationService:
    def __init__(
        self, api_key: str, model: str = "google/gemini-2.5-flash-preview-05-20"
    ):
        self.api_key = api_key
        self.model = model
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def upload_image_to_imgbb(self, image_bytes: bytes, api_key: str) -> str:
        url = "https://api.imgbb.com/1/upload"
        b64_image = base64.b64encode(image_bytes).decode("utf-8")
        payload = {"key": api_key, "image": b64_image}
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response.json()["data"]["url"]

    def extract_sentences_with_positions(self, image_url: str) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://www.google.com",
            "X-Title": "Google",
        }
        prompt = (
            "Analyze this image, split it into sentences or paragraphs. "
            "Return a JSON object with key 'text' as a list, each element is a dict: "
            "{'text': <content>, 'x': <x coordinate>, 'y': <y coordinate>}"
        )
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
        }
        response = requests.post(self.url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        result = json.loads(content)
        return result
