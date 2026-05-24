from form_check.rules.rule_utils import (
    avg_valid,
    torso_lean_from_vertical,
    calculate_score,
)


class RomanianDeadliftRules:
    def __init__(
        self,
        hinge_down_torso_threshold=35,
        stand_torso_threshold=15,
        max_knee_bend_angle=125,
    ):
        self.hinge_down_torso_threshold = hinge_down_torso_threshold
        self.stand_torso_threshold = stand_torso_threshold
        self.max_knee_bend_angle = max_knee_bend_angle

        self.rep_count = 0
        self.stage = "up"
        self.was_down = False

    def reset(self):
        self.rep_count = 0
        self.stage = "up"
        self.was_down = False

    def check(self, keypoints, angles):
        errors = []

        if keypoints is None or angles is None:
            return self._result([{"code": "no_pose", "severity": "high"}], {})

        torso_lean = torso_lean_from_vertical(keypoints)
        knee_avg = avg_valid([angles.get("left_knee"), angles.get("right_knee")])
        hip_avg = avg_valid([angles.get("left_hip"), angles.get("right_hip")])

        if torso_lean is None or knee_avg is None:
            return self._result([{"code": "no_pose", "severity": "high"}], {})

        # Rep counting for hinge
        if torso_lean > self.hinge_down_torso_threshold:
            self.stage = "down"
            self.was_down = True

        elif torso_lean < self.stand_torso_threshold:
            if self.was_down:
                self.rep_count += 1
            self.stage = "up"
            self.was_down = False

        else:
            self.stage = "middle"

        # RDL: không được squat quá nhiều
        # knee angle càng nhỏ nghĩa là gối gập càng nhiều
        if knee_avg < self.max_knee_bend_angle:
            errors.append({"code": "too_much_knee_bend", "severity": "medium"})
            errors.append({"code": "squatting_instead_of_hinging", "severity": "medium"})

        # Lưu ý: MediaPipe 2D khó detect cong lưng thật sự.
        # Tạm dùng torso lean quá lớn như proxy.
        if torso_lean > 65:
            errors.append({"code": "rounded_back", "severity": "high"})

        metrics = {
            "torso_lean": torso_lean,
            "knee_avg": knee_avg,
            "hip_avg": hip_avg,
        }

        return self._result(errors, metrics)

    def _result(self, errors, metrics):
        return {
            "exercise": "romanian_deadlift",
            "rep_count": self.rep_count,
            "stage": self.stage,
            "errors": errors,
            "metrics": metrics,
            "score": calculate_score(errors),
        }


class DeadliftRules(RomanianDeadliftRules):
    def _result(self, errors, metrics):
        return {
            "exercise": "deadlift",
            "rep_count": self.rep_count,
            "stage": self.stage,
            "errors": errors,
            "metrics": metrics,
            "score": calculate_score(errors),
        }
