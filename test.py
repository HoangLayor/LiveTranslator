import requests
import json

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": "Bearer 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",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://www.google.com", # Optional. Site URL for rankings on openrouter.ai.
    "X-Title": "Google", # Optional. Site title for rankings on openrouter.ai.
  },
  data=json.dumps({
    "model": "google/gemini-2.0-flash-001",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Extract all text content with their exact coordinates from this image"
          },
          {
            "type": "image_url",
            "image_url": {
              "url": "https://res.cloudinary.com/dw9bbrnke/image/upload/v1749026020/translation_20250604_153336.jpg"
            }
          }
        ]
      }
    ],
    
  })
)
print(response.json())