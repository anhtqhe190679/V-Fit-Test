import cv2
import json
from ui import draw_ui
from gemini_service import scan_food


def start_camera():
    last_result = {
        "food_name": "No scan yet",
        "total_calories": 0,
        "protein_g": 0,
        "carbs_g": 0,
        "fat_g": 0,
        "confidence": 0
    }

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Cannot open camera")
        return

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame = cv2.flip(frame, 1)
        display = draw_ui(frame.copy(), last_result)

        cv2.imshow("V-FIT Food Scanner", display)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            print("Scanning...")

            try:
                last_result = scan_food(frame)
                print(json.dumps(last_result, indent=2, ensure_ascii=False))

            except Exception as e:
                print("Scan error:", e)
                last_result["food_name"] = "Scan error"

        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()