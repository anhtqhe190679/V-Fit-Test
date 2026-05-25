import cv2
import json
import base64
import requests
from config import GEMINI_API_KEY, GEMINI_URL


def frame_to_base64(frame):
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode("utf-8")


def clean_json(text):
    return text.replace("```json", "").replace("```", "").strip()


def scan_food(frame):
    image_base64 = frame_to_base64(frame)

    prompt = """
Analyze the food image and estimate calories.

Return ONLY valid JSON:
{
  "food_name": "",
  "items": [],
  "total_calories": 0,
  "protein_g": 0,
  "carbs_g": 0,
  "fat_g": 0,
  "confidence": 0
}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_base64
                        }
                    }
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }

    response = requests.post(GEMINI_URL, headers=headers, json=payload, timeout=60)

    if response.status_code != 200:
        raise Exception(response.text)

    data = response.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"]

    return json.loads(clean_json(text))