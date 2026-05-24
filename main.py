import cv2
from shared.pose_estimation import PoseEstimator
from shared.keypoint_utils import extract_keypoints
from shared.angle_calculator import calculate_body_angles
from shared.drawing_utils import (
    draw_pose_landmarks,
    draw_keypoint_names,
    draw_angles,
    draw_form_result,
)

from body_analysis.body_analyzer import BodyAnalyzer


def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open laptop camera.")
        return

    pose_estimator = PoseEstimator()
    body_analyzer = BodyAnalyzer()
    
    # 1. KHỞI TẠO BIẾN TRƯỚC VÒNG LẶP (Chỉ khởi tạo 1 lần)
    frame_counter = 0
    current_body_type = "Analyzing..."
    current_desc = ""

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame.")
            break

        # Lật khung hình như gương để dễ nhìn
        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape

        # 2. Pose estimation & Extract keypoints
        results = pose_estimator.detect(frame)
        keypoints = extract_keypoints(results, width, height)

        # 3. Calculate angles & Analyze Body
        angles = None
        if keypoints is not None:
            angles = calculate_body_angles(keypoints)
            
            # Chỉ phân tích body 30 frame một lần (tránh giật lag)
            if frame_counter % 30 == 0:
                report = body_analyzer.generate_report(landmarks=keypoints, body_measurements=None)
                
                if report and report.get("status") == "success":
                    current_body_type = report.get("body_type", "Unknown")
                    current_desc = report.get("general_description", "")

        frame_counter += 1

        # 4. Draw pose results
        draw_pose_landmarks(frame, results)
        draw_keypoint_names(frame, keypoints)
        draw_angles(frame, keypoints, angles)
        draw_form_result(frame, form_result)

        # 5. HIỂN THỊ THÔNG TIN LÊN MÀN HÌNH
        # Nút thoát
        cv2.putText(
            frame, "Press Q to quit", (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA
        )
        
        # Dáng người
        cv2.putText(
            frame, f"Shape: {current_body_type}", (20, 80), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2, cv2.LINE_AA
        )

        # Lời khuyên / Mô tả chi tiết (nếu có)
        if current_desc:
            cv2.putText(
                frame, f"Note: {current_desc}", (20, 115), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA
            )

        cv2.imshow("AI Fitness Form Check", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    # 6. Dọn dẹp bộ nhớ
    pose_estimator.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()