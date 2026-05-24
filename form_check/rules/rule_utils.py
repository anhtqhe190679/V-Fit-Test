# form_check/rules/rule_utils.py

import math


def valid_angle(angle):
    return angle is not None and not math.isnan(angle)


def avg_valid(values):
    valid_values = [v for v in values if valid_angle(v)]
    if not valid_values:
        return None
    return sum(valid_values) / len(valid_values)


def point(keypoints, name):
    if keypoints is None:
        return None

    p = keypoints.get(name)
    if p is None:
        return None

    return [p["x"], p["y"]]


def midpoint(p1, p2):
    if p1 is None or p2 is None:
        return None

    return [
        (p1[0] + p2[0]) / 2,
        (p1[1] + p2[1]) / 2,
    ]


def distance(p1, p2):
    if p1 is None or p2 is None:
        return None

    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def torso_lean_from_vertical(keypoints):
    left_shoulder = point(keypoints, "left_shoulder")
    right_shoulder = point(keypoints, "right_shoulder")
    left_hip = point(keypoints, "left_hip")
    right_hip = point(keypoints, "right_hip")

    shoulder_center = midpoint(left_shoulder, right_shoulder)
    hip_center = midpoint(left_hip, right_hip)

    if shoulder_center is None or hip_center is None:
        return None

    dx = shoulder_center[0] - hip_center[0]
    dy = shoulder_center[1] - hip_center[1]

    if dy == 0:
        return 90.0

    return math.degrees(math.atan2(abs(dx), abs(dy)))


def shoulder_hip_shift(keypoints):
    left_shoulder = point(keypoints, "left_shoulder")
    right_shoulder = point(keypoints, "right_shoulder")
    left_hip = point(keypoints, "left_hip")
    right_hip = point(keypoints, "right_hip")

    shoulder_center = midpoint(left_shoulder, right_shoulder)
    hip_center = midpoint(left_hip, right_hip)

    if shoulder_center is None or hip_center is None:
        return None

    return abs(shoulder_center[0] - hip_center[0])


def shoulder_balance_diff(keypoints):
    left_shoulder = point(keypoints, "left_shoulder")
    right_shoulder = point(keypoints, "right_shoulder")

    if left_shoulder is None or right_shoulder is None:
        return None

    return abs(left_shoulder[1] - right_shoulder[1])


def hip_balance_diff(keypoints):
    left_hip = point(keypoints, "left_hip")
    right_hip = point(keypoints, "right_hip")

    if left_hip is None or right_hip is None:
        return None

    return abs(left_hip[1] - right_hip[1])


def knee_inward_check(keypoints):
    left_knee = point(keypoints, "left_knee")
    right_knee = point(keypoints, "right_knee")
    left_ankle = point(keypoints, "left_ankle")
    right_ankle = point(keypoints, "right_ankle")

    if left_knee is None or right_knee is None or left_ankle is None or right_ankle is None:
        return False

    knee_distance = abs(left_knee[0] - right_knee[0])
    ankle_distance = abs(left_ankle[0] - right_ankle[0])

    if ankle_distance < 40:
        return False

    return knee_distance < ankle_distance * 0.75


def calculate_score(errors):
    score = 100

    for error in errors:
        severity = error.get("severity", "low")

        if severity == "high":
            score -= 25
        elif severity == "medium":
            score -= 15
        else:
            score -= 5

    return max(score, 0)
