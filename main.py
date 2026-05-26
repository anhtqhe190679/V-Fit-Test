import cv2
import mediapipe as mp

from shared.angle_calculator import calculate_body_angles
from shared.drawing_utils import draw_unicode_text

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

def extract_keypoints(results, width, height):
    if not results.pose_landmarks:
        return None
    
    keypoints = {}
    for landmark in mp.solutions.pose.PoseLandmark:
        pt = results.pose_landmarks.landmark[landmark.value]
        keypoints[landmark.name.lower()] = {
            'x': pt.x * width,
            'y': pt.y * height,
            'visibility': pt.visibility
        }
    return keypoints

def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Could not open camera.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        model_complexity=2,           
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    )
    mp_drawing = mp.solutions.drawing_utils

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
    current_imbalances = []

    print_exercise_list()

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)
        
        keypoints = extract_keypoints(results, width, height)
        angles = None

        if keypoints is not None:
            angles = calculate_body_angles(keypoints)

            form_result = form_checker.check(keypoints, angles)

            if hasattr(body_analyzer, 'imbalance_detector'):
                current_imbalances = body_analyzer.imbalance_detector.detect_imbalance(keypoints)

            if frame_counter % 30 == 0:
                report = body_analyzer.generate_report(
                    landmarks=keypoints,
                    segmentation_mask=getattr(results, "segmentation_mask", None) 
                )
                if report and report.get("status") == "success":
                    current_body_type = report.get("body_type", "Unknown")
                    current_desc = report.get("general_description", "")
            
            mp_drawing.draw_landmarks(
                frame, 
                results.pose_landmarks, 
                mp_pose.POSE_CONNECTIONS
            )
        else:
            form_result = form_checker.check(None, None)
            current_imbalances = [] 
            current_body_type = "Khong co nguoi..." 
            current_desc = "" 

        frame_counter += 1
        current_name = get_exercise_name(current_exercise)

        # =========================================================
        # UI RENDERING
        # =========================================================
        info_y = 40
        
        draw_unicode_text(frame, f"Bai tap: {current_name} ({camera_view})", (20, info_y), font_size=20, color=(0, 255, 255), bold=True)
        info_y += 35
        draw_unicode_text(frame, f"Dang nguoi: {current_body_type}", (20, info_y), font_size=18, color=(255, 255, 0), bold=False)
        info_y += 35
        
        if current_desc:
            draw_unicode_text(frame, current_desc, (20, info_y), font_size=16, color=(255, 255, 255), bold=False)
            info_y += 35
            
        if form_result and isinstance(form_result, dict):
            feedbacks = form_result.get('feedback', [])
            for fb in feedbacks:
                warning = fb.get('warning', '')
                correction = fb.get('correction', '')
                
                if fb.get('code') == 'good_form':
                    draw_unicode_text(frame, f"Form: {warning}", (20, info_y), font_size=18, color=(0, 255, 0), bold=True)
                    info_y += 30
                else:
                    draw_unicode_text(frame, f"Loi: {warning}", (20, info_y), font_size=18, color=(0, 165, 255), bold=True)
                    info_y += 30
                    draw_unicode_text(frame, f"-> Sua: {correction}", (20, info_y), font_size=16, color=(255, 255, 255), bold=False)
                    info_y += 35

        y_offset = 340  
        if current_imbalances: 
            for issue in current_imbalances:
                color = (0, 255, 0) if ("THANG" in issue.upper() or "CAN" in issue.upper()) else (0, 0, 255)
                draw_unicode_text(
                    frame,
                    f"- {issue}",
                    (20, y_offset),
                    font_size=18,
                    color=color,
                    bold=False
                )
                y_offset += 35  
        else:
            draw_unicode_text(
                frame,
                "- Tu the: CAN DOI",
                (20, y_offset),
                font_size=18,
                color=(0, 255, 0), 
                bold=True
            )

        display_frame = cv2.resize(frame, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        cv2.imshow(WINDOW_NAME, display_frame)

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

    pose.close() 
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()