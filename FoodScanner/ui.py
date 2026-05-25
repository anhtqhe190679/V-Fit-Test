import cv2


def draw_ui(frame, result):
    h, w, _ = frame.shape

    cv2.rectangle(frame, (20, 20), (w - 20, 230), (0, 0, 0), -1)

    cv2.putText(frame, "V-FIT FOOD SCANNER", (40, 55),
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