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

from form_check.form_checker import FormChecker


EXERCISES = {
    ord("1"): "squat",
    ord("2"): "romanian_deadlift",
    ord("3"): "deadlift",
    ord("4"): "bicep_curl",
    ord("5"): "triceps_pushdown",
}


def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open laptop camera.")
        return

    pose_estimator = PoseEstimator()
    form_checker = FormChecker(exercise="squat", camera_view="side")

    print("Controls:")
    print("1 = squat")
    print("2 = romanian_deadlift")
    print("3 = deadlift")
    print("4 = bicep_curl")
    print("5 = triceps_pushdown")
    print("R = reset reps")
    print("Q = quit")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame.")
            break

        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape

        results = pose_estimator.detect(frame)
        keypoints = extract_keypoints(results, width, height)

        angles = None
        if keypoints is not None:
            angles = calculate_body_angles(keypoints)

        form_result = form_checker.check(keypoints, angles)

        draw_pose_landmarks(frame, results)
        draw_keypoint_names(frame, keypoints)
        draw_angles(frame, keypoints, angles)
        draw_form_result(frame, form_result)

        cv2.putText(
            frame,
            "1 Squat | 2 RDL | 3 Deadlift | 4 Curl | 5 Triceps | R Reset | Q Quit",
            (20, height - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        cv2.imshow("AI Fitness Form Check", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        if key == ord("r"):
            form_checker.reset()
            print("Reset reps.")

        if key in EXERCISES:
            exercise = EXERCISES[key]
            form_checker.set_exercise(exercise)
            print(f"Switched exercise to: {exercise}")

    pose_estimator.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
