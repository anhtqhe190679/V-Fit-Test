from form_check.rules.rule_utils import (
    avg_valid,
    valid_angle,
    torso_lean_from_vertical,
    knee_inward_check,
    calculate_score,
)


class SquatRules:
    def __init__(
        self,
        down_threshold=105,
        up_threshold=160,
        torso_lean_threshold=45,
        leg_imbalance_threshold=20,
        camera_view="side",
    ):
        self.down_threshold = down_threshold
        self.up_threshold = up_threshold
        self.torso_lean_threshold = torso_lean_threshold
        self.leg_imbalance_threshold = leg_imbalance_threshold
        self.camera_view = camera_view

        self.rep_count = 0
        self.stage = "up"
        self.was_down = False
        self.middle_frames = 0

    def reset(self):
        self.rep_count = 0
        self.stage = "up"
        self.was_down = False
        self.middle_frames = 0

    def check(self, keypoints, angles):
        errors = []

        if keypoints is None or angles is None:
            return self._result(errors=[{"code": "no_pose", "severity": "high"}], metrics={})

        left_knee = angles.get("left_knee")
        right_knee = angles.get("right_knee")
        left_hip = angles.get("left_hip")
        right_hip = angles.get("right_hip")

        knee_avg = avg_valid([left_knee, right_knee])
        hip_avg = avg_valid([left_hip, right_hip])
        torso_lean = torso_lean_from_vertical(keypoints)

        if knee_avg is None:
            return self._result(errors=[{"code": "no_pose", "severity": "high"}], metrics={})

        # Rep counting
        if knee_avg < self.down_threshold:
            self.stage = "down"
            self.was_down = True
            self.middle_frames = 0

        elif knee_avg > self.up_threshold:
            if self.was_down:
                self.rep_count += 1
            self.stage = "up"
            self.was_down = False
            self.middle_frames = 0

        else:
            self.stage = "middle"
            self.middle_frames += 1

        # Error 1: squat chưa đủ sâu
        if self.stage == "middle" and self.middle_frames > 8 and not self.was_down:
            errors.append({"code": "not_deep_enough", "severity": "medium"})

        # Error 2: nghiêng người quá nhiều
        if torso_lean is not None and torso_lean > self.torso_lean_threshold:
            errors.append({"code": "back_leaning_too_much", "severity": "medium"})

        # Error 3: hai chân không đều
        if valid_angle(left_knee) and valid_angle(right_knee):
            if abs(left_knee - right_knee) > self.leg_imbalance_threshold:
                errors.append({"code": "leg_imbalance", "severity": "medium"})

        # Error 4: gối chụm vào trong, tốt nhất dùng front view
        if self.camera_view == "front" and knee_avg < 150:
            if knee_inward_check(keypoints):
                errors.append({"code": "knee_inward", "severity": "high"})

        metrics = {
            "left_knee": left_knee,
            "right_knee": right_knee,
            "knee_avg": knee_avg,
            "left_hip": left_hip,
            "right_hip": right_hip,
            "hip_avg": hip_avg,
            "torso_lean": torso_lean,
        }

        return self._result(errors=errors, metrics=metrics)

    def _result(self, errors, metrics):
        return {
            "exercise": "squat",
            "rep_count": self.rep_count,
            "stage": self.stage,
            "errors": errors,
            "metrics": metrics,
            "score": calculate_score(errors),
        }
