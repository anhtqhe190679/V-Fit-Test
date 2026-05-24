import cv2

from shared.pose_estimation import PoseEstimator
from shared.keypoint_utils import extract_keypoints
from shared.angle_calculator import calculate_body_angles
from shared.drawing_utils import (
    draw_pose_landmarks,
    draw_keypoint_names,
    draw_angles,
    draw_form_result,
    draw_unicode_text,
)

from form_check.form_checker import FormChecker
from form_check.exercise_registry import EXERCISES, EXERCISE_SLUGS, get_exercise_name
from body_analysis.body_analyzer import BodyAnalyzer


# ============================================================
# Display config
# ============================================================

DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720

CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

WINDOW_NAME = "AI Fitness Form Check + Body Analysis"


def print_exercise_list():
    print("\n===== EXERCISE LIST =====")
    for i, item in enumerate(EXERCISES):
        print(f"{i + 1:02d}. {item['display_name']} ({item['slug']})")
    print("=========================\n")


def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open laptop camera.")
        return

    # Set camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

    # Make OpenCV window larger and resizable
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, DISPLAY_WIDTH, DISPLAY_HEIGHT)

    # Nếu muốn fullscreen thì mở comment 3 dòng dưới:
    # cv2.setWindowProperty(
    #     WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN
    # )

    pose_estimator = PoseEstimator()
    body_analyzer = BodyAnalyzer()

    exercise_index = 0
    current_exercise = EXERCISE_SLUGS[exercise_index]
    camera_view = "side"

    form_checker = FormChecker(
        exercise=current_exercise,
        camera_view=camera_view,
    )

    frame_counter = 0
    current_body_type = "Analyzing..."
    current_desc = ""

    print_exercise_list()
    print("Controls:")
    print("N = next exercise")
    print("P = previous exercise")
    print("R = reset reps")
    print("F = front view mode")
    print("S = side view mode")
    print("L = print exercise list")
    print("Q = quit")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame.")
            break

        # Mirror effect
        frame = cv2.flip(frame, 1)

        height, width, _ = frame.shape

        # 1. Pose estimation
        results = pose_estimator.detect(frame)

        # 2. Extract keypoints
        keypoints = extract_keypoints(results, width, height)

        # 3. Calculate angles + form check + body analysis
        angles = None

        if keypoints is not None:
            angles = calculate_body_angles(keypoints)

            # Người 1: AI Form Check
            form_result = form_checker.check(keypoints, angles)

            # Người 2: AI Body Analysis
            # Chạy mỗi 30 frame để tránh lag
            if frame_counter % 30 == 0:
                report = body_analyzer.generate_report(
                    landmarks=keypoints,
                    body_measurements=None,
                )

                if report and report.get("status") == "success":
                    current_body_type = report.get("body_type", "Unknown")
                    current_desc = report.get("general_description", "")
        else:
            form_result = form_checker.check(None, None)

        frame_counter += 1

        # 4. Draw pose results
        draw_pose_landmarks(frame, results)
        draw_keypoint_names(frame, keypoints)
        draw_angles(frame, keypoints, angles)

        # 5. Draw form check result
        draw_form_result(frame, form_result)

        # 6. Draw current exercise info
        current_name = get_exercise_name(current_exercise)

        draw_unicode_text(
            frame,
            f"Bài hiện tại: {exercise_index + 1}/{len(EXERCISE_SLUGS)} - {current_name}",
            (20, height - 105),
            font_size=22,
            color=(0, 255, 255),
            bold=True,
        )

        draw_unicode_text(
            frame,
            f"View: {camera_view} | N: bài tiếp | P: bài trước | R: reset | F: front | S: side | Q: thoát",
            (20, height - 72),
            font_size=19,
            color=(255, 255, 255),
            bold=False,
        )

        # 7. Draw body analysis result
        draw_unicode_text(
            frame,
            f"Body Shape: {current_body_type}",
            (20, 270),
            font_size=22,
            color=(255, 255, 0),
            bold=True,
        )

        if current_desc:
            draw_unicode_text(
                frame,
                f"Body Note: {current_desc}",
                (20, 305),
                font_size=18,
                color=(0, 255, 255),
                bold=False,
            )

        # 8. Resize display window
        display_frame = cv2.resize(frame, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        cv2.imshow(WINDOW_NAME, display_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        if key == ord("r"):
            form_checker.reset()
            print("Reset reps.")

        if key == ord("l"):
            print_exercise_list()

        if key == ord("f"):
            camera_view = "front"
            form_checker.set_camera_view(camera_view)
            print("Switched to front view.")

        if key == ord("s"):
            camera_view = "side"
            form_checker.set_camera_view(camera_view)
            print("Switched to side view.")

        if key == ord("n"):
            exercise_index = (exercise_index + 1) % len(EXERCISE_SLUGS)
            current_exercise = EXERCISE_SLUGS[exercise_index]

            form_checker = FormChecker(
                exercise=current_exercise,
                camera_view=camera_view,
            )

            print(
                f"Switched to: {exercise_index + 1}. "
                f"{get_exercise_name(current_exercise)}"
            )

        if key == ord("p"):
            exercise_index = (exercise_index - 1) % len(EXERCISE_SLUGS)
            current_exercise = EXERCISE_SLUGS[exercise_index]

            form_checker = FormChecker(
                exercise=current_exercise,
                camera_view=camera_view,
            )

            print(
                f"Switched to: {exercise_index + 1}. "
                f"{get_exercise_name(current_exercise)}"
            )

    pose_estimator.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
