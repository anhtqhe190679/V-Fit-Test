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
# Config & State
# ============================================================
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
WINDOW_NAME = "V-FIT AI Coach"

# Quản lý trạng thái: "SCAN_BODY" -> "RECOMMEND" -> "WORKOUT"
APP_STAGE = "SCAN_BODY" 

SAVED_BODY_TYPE = None
SAVED_BODY_DESC = None
RECOMMENDED_EXERCISES = []

# Biến đếm frame toàn cục
frame_counter = 0 
COUNTDOWN_TOTAL_FRAMES = 90 

def get_recommendations(body_type):
    """
    Hàm gợi ý bài tập khớp chuẩn xác với kết quả từ AI Model Deep Learning
    """
    recommendations = []
    if not body_type:
        return ["squat", "bicep_curl", "barbell_bench_press", "pull_up"]
        
    body_type_upper = body_type.upper()
    
    if "CHU V" in body_type_upper:
        recommendations = ["squat", "dumbbell_lateral_raise", "romanian_deadlift"]
    elif "QUA LE" in body_type_upper:
        recommendations = ["squat", "deadlift", "leg_press", "pull_up"]
    elif "CHU NHAT" in body_type_upper:
        recommendations = ["squat", "bicep_curl", "barbell_bench_press", "pull_up"]
    else:
        recommendations = ["squat", "bicep_curl", "barbell_bench_press", "pull_up"]
        
    return recommendations

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
    global APP_STAGE, SAVED_BODY_TYPE, SAVED_BODY_DESC, RECOMMENDED_EXERCISES, frame_counter
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open camera.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    mp_pose = mp.solutions.pose
    # Bổ sung thêm enable_segmentation=True vào cuối
    pose = mp_pose.Pose(
        model_complexity=2, 
        min_detection_confidence=0.6, 
        min_tracking_confidence=0.6,
        enable_segmentation=True 
    )
    mp_drawing = mp.solutions.drawing_utils
    body_analyzer = BodyAnalyzer()
    
    exercise_index = 0
    current_exercise = EXERCISE_SLUGS[exercise_index]
    camera_view = "side"
    form_checker = FormChecker(exercise=current_exercise, camera_view=camera_view)

    current_imbalances = []
    countdown_counter = COUNTDOWN_TOTAL_FRAMES

    print("\n>>> UNG DUNG KHIEN HANH: GIAIDOAN 1 - QUET DANG NGUOI <<<")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)
        keypoints = extract_keypoints(results, width, height)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        if APP_STAGE == "RECOMMEND":
            cv2.rectangle(frame, (0, 0), (width, height), (30, 30, 30), -1)

        # =========================================================================
        # GIAI DOAN 1: QUET DANG NGUOI VỚI CƠ CHẾ ĐẾM NGƯỢC
        # =========================================================================
        if APP_STAGE == "SCAN_BODY":
            has_valid_points = False
            if keypoints is not None:
                l_shoulder = keypoints.get('left_shoulder')
                r_shoulder = keypoints.get('right_shoulder')
                l_hip = keypoints.get('left_hip')
                r_hip = keypoints.get('right_hip')
                if all([l_shoulder, r_shoulder, l_hip, r_hip]):
                    has_valid_points = True

            if has_valid_points:
                countdown_counter -= 1
                seconds_left = max(1, int(countdown_counter / 30) + 1)
                
                # Hiển thị số giây đếm ngược siêu to giữa màn hình
                cv2.putText(frame, str(seconds_left), (int(width/2) - 30, int(height/2) + 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 255, 255), 8, cv2.LINE_AA)
                
                draw_unicode_text(frame, f"Da tim thay co the! Chuan bi quet trong: {seconds_left}s", (20, 40), font_size=20, color=(0, 255, 0), bold=True)
                draw_unicode_text(frame, "Hay dung vung va giu nguyen tu the...", (20, 75), font_size=16, color=(200, 200, 200), bold=False)

                if countdown_counter <= 0:
                    # Rút mặt nạ bóc tách hình thể thực tế an toàn bằng hàm getattr
                    mask_data = getattr(results, "segmentation_mask", None)
                    
                    # [ĐA SỬA CHUẨN ĐỒNG BỘ]: Gọi chính xác từ khóa 'landmarks' theo cấu trúc phân tích lõi
                    report = body_analyzer.generate_report(frame=frame, landmarks=keypoints, segmentation_mask=mask_data)
                    
                    if report and report.get("status") == "success":
                        # Đồng bộ key 'body_shape' lấy từ kết quả trích xuất của Model AI
                        SAVED_BODY_TYPE = report.get("body_shape", "Chua xac dinh")
                        SAVED_BODY_DESC = report.get("general_description", "Phan tich boi AI Deep Learning")
                        
                        RECOMMENDED_EXERCISES = get_recommendations(SAVED_BODY_TYPE)
                        APP_STAGE = "RECOMMEND"
                        print(f"\n[AI] Da luu dang nguoi: {SAVED_BODY_TYPE}")
                    else:
                        # Nếu trạm điều phối báo lỗi ngầm, in log ra Terminal để debug dễ dàng
                        print(f"[DEBUG LỖI AI]: {report.get('message') if report else 'Không nhận được báo cáo'}")
                        # Reset lại bộ đếm để người dùng thử quét lại ở frame tiếp theo
                        countdown_counter = COUNTDOWN_TOTAL_FRAMES
            else:
                countdown_counter = COUNTDOWN_TOTAL_FRAMES
                draw_unicode_text(frame, "Hay dung sao cho camera thay ro tu Vai den Hong de bat dau", (20, 40), font_size=20, color=(0, 0, 255), bold=True)

        # =========================================================================
        # GIAI DOAN 2: GOI Y BAI TAP (RECOMMENDATION MENU)
        # =========================================================================
        elif APP_STAGE == "RECOMMEND":
            draw_unicode_text(frame, "--- KET QUA QUET DANG NGUOI ---", (20, 40), font_size=22, color=(0, 255, 255), bold=True)
            draw_unicode_text(frame, f"Dang cua ban: {SAVED_BODY_TYPE}", (20, 85), font_size=18, color=(0, 255, 0), bold=True)
            draw_unicode_text(frame, f"Chi tiet: {SAVED_BODY_DESC}", (20, 120), font_size=16, color=(255, 255, 255), bold=False)
            
            draw_unicode_text(frame, "--- AI RECOMMENDATION (BAI TAP GOI Y) ---", (20, 180), font_size=20, color=(255, 255, 0), bold=True)
            
            y_pos = 220
            for idx, ex_slug in enumerate(RECOMMENDED_EXERCISES):
                is_selected = (idx == exercise_index % len(RECOMMENDED_EXERCISES))
                color = (0, 255, 0) if is_selected else (200, 200, 200)
                prefix = "-> [ " if is_selected else "   [ "
                suffix = " ]" if is_selected else ""
                
                ex_name = get_exercise_name(ex_slug)
                draw_unicode_text(frame, f"{prefix}{idx+1}. {ex_name}{suffix}", (40, y_pos), font_size=18, color=color, bold=is_selected)
                y_pos += 40
                
            draw_unicode_text(frame, "An [N] / [P] de chon bai - An [ENTER] de BAT DAU TAP LUYEN", (20, height - 50), font_size=16, color=(100, 255, 100), bold=False)

        # =========================================================================
        # GIAI DOAN 3: SUA DANG TAP TIME-REAL
        # =========================================================================
        elif APP_STAGE == "WORKOUT":
            if keypoints is not None:
                form_result = form_checker.check(keypoints, calculate_body_angles(keypoints))
                if hasattr(body_analyzer, 'imbalance_detector'):
                    current_imbalances = body_analyzer.imbalance_detector.detect_imbalance(keypoints)
            else:
                form_result = form_checker.check(None, None)
                current_imbalances = []

            info_y = 40
            current_name = get_exercise_name(current_exercise)
            draw_unicode_text(frame, "Che do: LUYEN TAP TIME-REAL", (20, info_y), font_size=16, color=(255, 255, 255), bold=False)
            info_y += 25
            draw_unicode_text(frame, f"Bai tap dang chon: {current_name} ({camera_view})", (20, info_y), font_size=20, color=(0, 255, 255), bold=True)
            info_y += 35
            draw_unicode_text(frame, f"Dang nguoi goc: {SAVED_BODY_TYPE}", (20, info_y), font_size=16, color=(255, 255, 0), bold=False)
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
                        draw_unicode_text(frame, f"-> Huong dan: {correction}", (20, info_y), font_size=16, color=(255, 255, 255), bold=False)
                        info_y += 35

            y_offset = 380  
            if current_imbalances:
                for issue in current_imbalances:
                    color = (0, 255, 0) if ("THANG" in issue.upper() or "CAN" in issue.upper()) else (0, 0, 255)
                    draw_unicode_text(frame, f"- {issue}", (20, y_offset), font_size=18, color=color, bold=False)
                    y_offset += 35  
            else:
                draw_unicode_text(frame, "- Tu the than nguoi: CAN DOI", (20, y_offset), font_size=18, color=(0, 255, 0), bold=True)

            draw_unicode_text(frame, "An [B] de quay lai Menu chon bai tap", (20, height - 40), font_size=14, color=(150, 150, 150), bold=False)

        frame_counter += 1
        display_frame = cv2.resize(frame, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
        cv2.imshow(WINDOW_NAME, display_frame)

        # =========================================================================
        # KEY EVENTS
        # =========================================================================
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
            
        elif APP_STAGE == "RECOMMEND":
            if key == ord("n"):
                exercise_index = (exercise_index + 1) % len(RECOMMENDED_EXERCISES)
            elif key == ord("p"):
                exercise_index = (exercise_index - 1) % len(RECOMMENDED_EXERCISES)
            elif key == 13: # Phím ENTER
                current_exercise = RECOMMENDED_EXERCISES[exercise_index % len(RECOMMENDED_EXERCISES)]
                form_checker = FormChecker(exercise=current_exercise, camera_view=camera_view)
                APP_STAGE = "WORKOUT"
                
        elif APP_STAGE == "WORKOUT":
            if key == ord("r"):
                form_checker.reset()
            elif key == ord("f"):
                camera_view = "front"
                form_checker.set_camera_view(camera_view)
            elif key == ord("s"):
                camera_view = "side"
                form_checker.set_camera_view(camera_view)
            elif key == ord("b"):
                countdown_counter = COUNTDOWN_TOTAL_FRAMES
                APP_STAGE = "RECOMMEND"

    pose.close()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()