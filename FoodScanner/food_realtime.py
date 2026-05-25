import os
import cv2
import json
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MODEL = "gemini-2.5-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


last_result = {
    "food_name": "No scan yet",
    "total_calories": 0,
    "protein_g": 0,
    "carbs_g": 0,
    "fat_g": 0
}


def frame_to_base64(frame):
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode("utf-8")


def clean_json(text):
    text = text.strip()
    text = text.replace("```json", "").replace("```", "")
    return text.strip()


def scan_food_with_gemini(frame):
    image_base64 = frame_to_base64(frame)

    prompt = """
You are a food calorie estimation AI.

Analyze the food in this image.

Return ONLY valid JSON. No markdown. No explanation.

JSON format:
{
  "food_name": "name of the main food",
  "items": [
    {
      "name": "food item",
      "estimated_grams": number,
      "calories": number,
      "protein_g": number,
      "carbs_g": number,
      "fat_g": number
    }
  ],
  "total_calories": number,
  "protein_g": number,
  "carbs_g": number,
  "fat_g": number,
  "confidence": number
}

Rules:
- Estimate portion size from the image.
- If unsure, still make a reasonable estimate.
- Use common nutrition values.
- confidence is from 0 to 1.
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

    response = requests.post(URL, headers=headers, json=payload, timeout=60)

    if response.status_code != 200:
        raise Exception(response.text)

    data = response.json()

    text = data["candidates"][0]["content"]["parts"][0]["text"]
    text = clean_json(text)

    return json.loads(text)


def draw_ui(frame, result):
    h, w, _ = frame.shape

    cv2.rectangle(frame, (20, 20), (w - 20, 230), (0, 0, 0), -1)

    cv2.putText(frame, "V-FIT GEMINI FOOD SCANNER", (40, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    cv2.putText(frame, f"Food: {result.get('food_name', '-')}", (40, 95),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)

    cv2.putText(frame, f"Calories: {result.get('total_calories', 0)} kcal", (40, 130),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.putText(frame,
                f"P: {result.get('protein_g', 0)}g | C: {result.get('carbs_g', 0)}g | F: {result.get('fat_g', 0)}g",
                (40, 165),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.putText(frame, f"Confidence: {round(result.get('confidence', 0) * 100, 1)}%",
                (40, 200),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.putText(frame, "Press S to scan | Q to quit", (40, h - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

    return frame


def main():
    global last_result

    if not GEMINI_API_KEY:
        print("Missing GEMINI_API_KEY in .env")
        return

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Cannot open camera")
        return

    print("Camera opened")
    print("Press S to scan")
    print("Press Q to quit")

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame = cv2.flip(frame, 1)
        display = draw_ui(frame.copy(), last_result)
        cv2.imshow("V-FIT Gemini Food Scanner", display)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            print("Scanning...")

            try:
                result = scan_food_with_gemini(frame)
                last_result = result
                print(json.dumps(result, indent=2, ensure_ascii=False))

            except Exception as e:
                print("Error:", e)
                last_result = {
                    "food_name": "Scan error",
                    "total_calories": 0,
                    "protein_g": 0,
                    "carbs_g": 0,
                    "fat_g": 0,
                    "confidence": 0
                }

        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()