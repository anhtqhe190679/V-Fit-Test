import cv2

from shared.pose_estimation import PoseEstimator
from shared.keypoint_utils import extract_keypoints
from shared.angle_calculator import calculate_body_angles
from shared.drawing_utils import (
    draw_pose_landmarks,
    draw_unicode_text,
)

from form_check.form_checker import FormChecker
from form_check.exercise_registry import (
    EXERCISES,
    EXERCISE_SLUGS,
    get_exercise_name,
)
from body_analysis.body_analyzer import BodyAnalyzer

# ============================================================
# Display config
# ============================================================

DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720

CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

WINDOW_NAME = "V-FIT AI Coach"

def print_exercise_list():
    print("\n===== EXERCISE LIST =====")
    for i, item in enumerate(EXERCISES):
        print(f"{i+1:02d}. {item['display_name']} ({item['slug']})")
    print("=========================\n")

def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Could not open camera.")
        return

    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        CAMERA_WIDTH,
    )
    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        CAMERA_HEIGHT,
    )

    cv2.namedWindow(
        WINDOW_NAME,
        cv2.WINDOW_NORMAL,
    )

    pose_estimator = PoseEstimator()
    body_analyzer = BodyAnalyzer()

    exercise_index = 0
    current_exercise = EXERCISE_SLUGS[exercise_index]
    camera_view = "side"

    form_checker = FormChecker(
        exercise=current_exercise,
        camera_view=camera_view,
    )

    # Khởi tạo biến lưu trữ trạng thái hiển thị
    frame_counter = 0
    current_body_type = "Analyzing..."
    current_desc = ""
    current_imbalances = []

    print_exercise_list()

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape

        results = pose_estimator.detect(frame)
        keypoints = extract_keypoints(
            results,
            width,
            height,
        )

        angles = None

        if keypoints is not None:
            angles = calculate_body_angles(
                keypoints
            )

            # Luồng 1: AI Form Check (Chạy liên tục mỗi frame phục vụ đếm reps)
            form_result = form_checker.check(keypoints, angles)

            # Luồng 2: Đo lệch tư thế THỜI GIAN THỰC (Giải phóng hoàn toàn để chạy liên tục)
            if hasattr(body_analyzer, 'imbalance_detector'):
                current_imbalances = body_analyzer.imbalance_detector.detect_imbalance(keypoints)

            # Luồng 3: AI Quét dáng người nặng (Chạy định kỳ mỗi 30 frame tránh lag CPU)
            if frame_counter % 30 == 0:
                report = body_analyzer.generate_report(
                    landmarks=keypoints,
                    segmentation_mask=getattr(results, "segmentation_mask", None) 
                )
                if report and report.get("status") == "success":
                    current_body_type = report.get("body_type", "Unknown")
                    current_desc = report.get("general_description", "")
                    # KHÔNG đọc hay gán đè biến current_imbalances ở đây nữa để tránh kẹt bộ nhớ đóng băng
        else:
            form_result = form_checker.check(None, None)
            current_imbalances = [] # Xóa sạch danh sách lệch khi mất người
            current_body_type = "Khong co nguoi..." # Xóa chữ báo dáng người
            current_desc = "" # Xóa chữ mô tả

        # Draw skeleton only
        draw_pose_landmarks(
            frame,
            results,
        )

        # New UI
        current_name = get_exercise_name(
            current_exercise
        )

        # 7. Draw body analysis result (Shape & Note)
        draw_unicode_text(
            frame,
            form_result,
            current_name,
            camera_view,
            current_body_type,
            current_desc,
        )

        display_frame = cv2.resize(
            frame,
            (
                DISPLAY_WIDTH,
                DISPLAY_HEIGHT,
            ),
        )

        # 8. Draw Imbalance Issues (Lỗi lệch vai, hông, nghiêng đầu, cổ rùa...)
        y_offset = 340  # Bắt đầu vẽ ngay dưới Body Note
        
        if current_imbalances:  # Nếu danh sách chứa lỗi lệch (không rỗng)
            for issue in current_imbalances:
                # Nếu chuỗi chứa chữ "THANG" hoặc "CAN DOI" thì vẽ màu xanh lá, ngược lại vẽ màu đỏ cảnh báo
                color = (0, 255, 0) if ("THANG" in issue or "CAN" in issue) else (0, 0, 255)
                draw_unicode_text(
                    frame,
                    f"- {issue}",
                    (20, y_offset),
                    font_size=18,
                    color=color,
                    bold=False
                )
                y_offset += 35  # Tự động xuống dòng cho lỗi tiếp theo
        else:
            # Khi tất cả các trục vai, hông, cổ đều thẳng tuyệt đối (danh sách [] trống hoàn toàn)
            draw_unicode_text(
                frame,
                "- Tư thế: CÂN ĐỐI",
                (20, y_offset),
                font_size=18,
                color=(0, 255, 0),    # Màu XANH LÁ biểu thị trạng thái chuẩn form
                bold=True
            )

        # 9. Resize display window
        display_frame = cv2.resize(frame, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        cv2.imshow(WINDOW_NAME, display_frame)

        # 10. Key events (Tối ưu bằng elif)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break
        elif key == ord("r"):
            form_checker.reset()
            print("Reset reps.")
        elif key == ord("l"):
            print_exercise_list()
        elif key == ord("f"):
            camera_view = "front"
            form_checker.set_camera_view(camera_view)
            print("Switched to front view.")
        elif key == ord("s"):
            camera_view = "side"
            form_checker.set_camera_view(camera_view)
            print("Switched to side view.")
        elif key == ord("n"):
            exercise_index = (exercise_index + 1) % len(EXERCISE_SLUGS)
            current_exercise = EXERCISE_SLUGS[exercise_index]
            form_checker = FormChecker(exercise=current_exercise, camera_view=camera_view)
            print(f"Switched to: {exercise_index + 1}. {get_exercise_name(current_exercise)}")
        elif key == ord("p"):
            exercise_index = (exercise_index - 1) % len(EXERCISE_SLUGS)
            current_exercise = EXERCISE_SLUGS[exercise_index]
            form_checker = FormChecker(exercise=current_exercise, camera_view=camera_view)
            print(f"Switched to: {exercise_index + 1}. {get_exercise_name(current_exercise)}")

    # Cleanup
    pose_estimator.close()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()