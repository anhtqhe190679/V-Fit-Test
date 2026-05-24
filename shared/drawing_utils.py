import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def draw_pose_landmarks(frame, results):
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
        )


def draw_keypoint_names(frame, keypoints):
    if keypoints is None:
        return

    for name, point in keypoints.items():
        x = point["x"]
        y = point["y"]

        cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)
        cv2.putText(
            frame,
            name,
            (x + 5, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )


def draw_angles(frame, keypoints, angles):
    if keypoints is None or angles is None:
        return

    positions = {
        "left_knee": "left_knee",
        "right_knee": "right_knee",
        "left_hip": "left_hip",
        "right_hip": "right_hip",
        "left_elbow": "left_elbow",
        "right_elbow": "right_elbow",
    }

    for angle_name, point_name in positions.items():
        if angle_name not in angles:
            continue

        if angles[angle_name] is None:
            continue

        point = keypoints.get(point_name)

        if point is None:
            continue

        x = point["x"]
        y = point["y"]

        cv2.putText(
            frame,
            f"{angle_name}: {angles[angle_name]:.1f}",
            (x + 10, y + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 255, 255),
            1,
            cv2.LINE_AA,
        )

def draw_form_result(frame, form_result):
    if form_result is None:
        return

    x = 20
    y = 40
    line_gap = 32

    exercise = form_result.get("exercise", "unknown")
    rep_count = form_result.get("rep_count", 0)
    stage = form_result.get("stage", "unknown")
    score = form_result.get("score", 0)
    feedback = form_result.get("feedback", [])

    cv2.rectangle(frame, (10, 10), (760, 230), (0, 0, 0), -1)

    cv2.putText(
        frame,
        f"Exercise: {exercise}",
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"Reps: {rep_count} | Stage: {stage} | Score: {score}",
        (x, y + line_gap),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2,
        cv2.LINE_AA,
    )

    if feedback:
        first = feedback[0]
        warning = first.get("warning", "")
        correction = first.get("correction", "")
        severity = first.get("severity", "low")

        color = (0, 255, 0)
        if severity == "medium":
            color = (0, 255, 255)
        elif severity == "high":
            color = (0, 0, 255)

        cv2.putText(
            frame,
            f"WARNING: {warning}",
            (x, y + line_gap * 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            color,
            2,
            cv2.LINE_AA,
        )

        cv2.putText(
            frame,
            f"FIX: {correction}",
            (x, y + line_gap * 3),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.58,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

    if len(feedback) > 1:
        second = feedback[1]
        cv2.putText(
            frame,
            f"NEXT: {second.get('correction', '')}",
            (x, y + line_gap * 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
