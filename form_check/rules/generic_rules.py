# form_check/rules/generic_rules.py

from form_check.rules.rule_utils import (
    avg_valid,
    valid_angle,
    point,
    distance,
    torso_lean_from_vertical,
    shoulder_hip_shift,
    shoulder_balance_diff,
    hip_balance_diff,
    knee_inward_check,
    calculate_score,
)


class BaseRule:
    def __init__(self, exercise="unknown", config=None):
        self.exercise = exercise
        self.config = config or {}

        self.rep_count = 0
        self.stage = "unknown"

        self.reached_low = False
        self.reached_high = False

        self.initial_left_elbow = None
        self.initial_right_elbow = None
        self.initial_left_shoulder = None
        self.initial_right_shoulder = None
        self.initial_hip_shift = None

    def reset(self):
        self.rep_count = 0
        self.stage = "unknown"
        self.reached_low = False
        self.reached_high = False

        self.initial_left_elbow = None
        self.initial_right_elbow = None
        self.initial_left_shoulder = None
        self.initial_right_shoulder = None
        self.initial_hip_shift = None

    def _result(self, errors, metrics):
        return {
            "exercise": self.exercise,
            "rep_count": self.rep_count,
            "stage": self.stage,
            "errors": errors,
            "metrics": metrics,
            "score": calculate_score(errors),
        }

    def _no_pose(self):
        return self._result(
            [{"code": "no_pose", "severity": "high"}],
            {},
        )

    def _update_rep_low_to_high(self, metric, low_threshold, high_threshold):
        """
        Example:
        squat/curl/press:
        reach low position first, then return high position = 1 rep
        """

        if metric is None:
            return

        if metric < low_threshold:
            self.stage = "low"
            self.reached_low = True

        elif metric > high_threshold:
            if self.reached_low:
                self.rep_count += 1

            self.stage = "high"
            self.reached_low = False

        else:
            self.stage = "middle"

    def _update_rep_high_to_low(self, metric, low_threshold, high_threshold):
        """
        Example:
        lateral raise/fly:
        raise high first, then lower back = 1 rep
        """

        if metric is None:
            return

        if metric > high_threshold:
            self.stage = "high"
            self.reached_high = True

        elif metric < low_threshold:
            if self.reached_high:
                self.rep_count += 1

            self.stage = "low"
            self.reached_high = False

        else:
            self.stage = "middle"

    def _elbow_avg(self, angles):
        return avg_valid([angles.get("left_elbow"), angles.get("right_elbow")])

    def _shoulder_avg(self, angles):
        return avg_valid([angles.get("left_shoulder"), angles.get("right_shoulder")])

    def _knee_avg(self, angles):
        return avg_valid([angles.get("left_knee"), angles.get("right_knee")])

    def _hip_avg(self, angles):
        return avg_valid([angles.get("left_hip"), angles.get("right_hip")])

    def _track_initial_points(self, keypoints):
        left_elbow = point(keypoints, "left_elbow")
        right_elbow = point(keypoints, "right_elbow")
        left_shoulder = point(keypoints, "left_shoulder")
        right_shoulder = point(keypoints, "right_shoulder")

        if self.initial_left_elbow is None and left_elbow is not None:
            self.initial_left_elbow = left_elbow

        if self.initial_right_elbow is None and right_elbow is not None:
            self.initial_right_elbow = right_elbow

        if self.initial_left_shoulder is None and left_shoulder is not None:
            self.initial_left_shoulder = left_shoulder

        if self.initial_right_shoulder is None and right_shoulder is not None:
            self.initial_right_shoulder = right_shoulder

    def _max_elbow_move(self, keypoints):
        left_elbow = point(keypoints, "left_elbow")
        right_elbow = point(keypoints, "right_elbow")

        left_move = distance(left_elbow, self.initial_left_elbow)
        right_move = distance(right_elbow, self.initial_right_elbow)

        values = [v for v in [left_move, right_move] if v is not None]
        return max(values) if values else 0

    def _body_shift(self, keypoints):
        value = shoulder_hip_shift(keypoints)
        return value if value is not None else 0


class SquatRule(BaseRule):
    def check(self, keypoints, angles):
        if keypoints is None or angles is None:
            return self._no_pose()

        errors = []

        left_knee = angles.get("left_knee")
        right_knee = angles.get("right_knee")
        knee_avg = self._knee_avg(angles)
        hip_avg = self._hip_avg(angles)
        torso_lean = torso_lean_from_vertical(keypoints)

        if knee_avg is None:
            return self._no_pose()

        self._update_rep_low_to_high(
            knee_avg,
            low_threshold=105,
            high_threshold=160,
        )

        if self.stage == "middle" and knee_avg > 120:
            errors.append({"code": "not_deep_enough", "severity": "medium"})

        if torso_lean is not None and torso_lean > 45:
            errors.append({"code": "back_leaning_too_much", "severity": "medium"})

        if valid_angle(left_knee) and valid_angle(right_knee):
            if abs(left_knee - right_knee) > 22:
                errors.append({"code": "leg_imbalance", "severity": "medium"})

        if knee_avg < 150 and knee_inward_check(keypoints):
            errors.append({"code": "knee_inward", "severity": "high"})

        return self._result(
            errors,
            {
                "knee_avg": knee_avg,
                "hip_avg": hip_avg,
                "torso_lean": torso_lean,
            },
        )


class HingeRule(BaseRule):
    def check(self, keypoints, angles):
        if keypoints is None or angles is None:
            return self._no_pose()

        errors = []

        torso_lean = torso_lean_from_vertical(keypoints)
        knee_avg = self._knee_avg(angles)
        hip_avg = self._hip_avg(angles)

        if torso_lean is None or knee_avg is None:
            return self._no_pose()

        self._update_rep_high_to_low(
            torso_lean,
            low_threshold=15,
            high_threshold=35,
        )

        if knee_avg < 125:
            errors.append({"code": "too_much_knee_bend", "severity": "medium"})

        if torso_lean > 65:
            errors.append({"code": "rounded_back", "severity": "high"})

        return self._result(
            errors,
            {
                "torso_lean": torso_lean,
                "knee_avg": knee_avg,
                "hip_avg": hip_avg,
            },
        )


class DeadliftRule(HingeRule):
    def check(self, keypoints, angles):
        result = super().check(keypoints, angles)

        # Deadlift allows more knee bend than RDL, so remove too_much_knee_bend if present.
        result["errors"] = [
            e for e in result["errors"]
            if e.get("code") != "too_much_knee_bend"
        ]
        result["score"] = calculate_score(result["errors"])
        return result


class CurlRule(BaseRule):
    def check(self, keypoints, angles):
        if keypoints is None or angles is None:
            return self._no_pose()

        self._track_initial_points(keypoints)

        errors = []

        elbow_avg = self._elbow_avg(angles)
        body_shift = self._body_shift(keypoints)
        elbow_move = self._max_elbow_move(keypoints)

        if elbow_avg is None:
            return self._no_pose()

        self._update_rep_low_to_high(
            elbow_avg,
            low_threshold=60,
            high_threshold=150,
        )

        if elbow_move > 55:
            errors.append({"code": "elbow_moving_too_much", "severity": "medium"})

        if body_shift > 55:
            errors.append({"code": "body_swing", "severity": "medium"})

        if self.stage == "middle" and 80 < elbow_avg < 135:
            errors.append({"code": "not_full_rom", "severity": "low"})

        return self._result(
            errors,
            {
                "elbow_avg": elbow_avg,
                "body_shift": body_shift,
                "elbow_move": elbow_move,
            },
        )


class TricepsExtensionRule(BaseRule):
    def check(self, keypoints, angles):
        if keypoints is None or angles is None:
            return self._no_pose()

        self._track_initial_points(keypoints)

        errors = []

        elbow_avg = self._elbow_avg(angles)
        body_shift = self._body_shift(keypoints)
        elbow_move = self._max_elbow_move(keypoints)

        if elbow_avg is None:
            return self._no_pose()

        self._update_rep_low_to_high(
            elbow_avg,
            low_threshold=80,
            high_threshold=155,
        )

        if elbow_move > 55:
            errors.append({"code": "elbow_moving_too_much", "severity": "medium"})

        if body_shift > 55:
            errors.append({"code": "body_swing", "severity": "medium"})

        if elbow_avg > 172:
            errors.append({"code": "elbow_locked_hard", "severity": "low"})

        return self._result(
            errors,
            {
                "elbow_avg": elbow_avg,
                "body_shift": body_shift,
                "elbow_move": elbow_move,
            },
        )


class PressRule(BaseRule):
    def check(self, keypoints, angles):
        if keypoints is None or angles is None:
            return self._no_pose()

        errors = []

        elbow_avg = self._elbow_avg(angles)
        shoulder_avg = self._shoulder_avg(angles)
        body_shift = self._body_shift(keypoints)
        shoulder_diff = shoulder_balance_diff(keypoints)

        if elbow_avg is None:
            return self._no_pose()

        self._update_rep_low_to_high(
            elbow_avg,
            low_threshold=85,
            high_threshold=155,
        )

        if shoulder_avg is not None and shoulder_avg > 155:
            errors.append({"code": "shoulder_compensation", "severity": "medium"})

        if body_shift > 65:
            errors.append({"code": "too_much_torso_movement", "severity": "medium"})

        if shoulder_diff is not None and shoulder_diff > 45:
            errors.append({"code": "leg_imbalance", "severity": "low"})

        if elbow_avg > 173:
            errors.append({"code": "elbow_locked_hard", "severity": "low"})

        return self._result(
            errors,
            {
                "elbow_avg": elbow_avg,
                "shoulder_avg": shoulder_avg,
                "body_shift": body_shift,
                "shoulder_diff": shoulder_diff,
            },
        )


class ShoulderPressRule(PressRule):
    pass


class FlyRule(BaseRule):
    def check(self, keypoints, angles):
        if keypoints is None or angles is None:
            return self._no_pose()

        self._track_initial_points(keypoints)

        errors = []

        shoulder_avg = self._shoulder_avg(angles)
        elbow_avg = self._elbow_avg(angles)
        body_shift = self._body_shift(keypoints)

        if shoulder_avg is None:
            return self._no_pose()

        self._update_rep_high_to_low(
            shoulder_avg,
            low_threshold=35,
            high_threshold=95,
        )

        if elbow_avg is not None and elbow_avg < 120:
            errors.append({"code": "elbow_moving_too_much", "severity": "medium"})

        if body_shift > 60:
            errors.append({"code": "body_swing", "severity": "medium"})

        return self._result(
            errors,
            {
                "shoulder_avg": shoulder_avg,
                "elbow_avg": elbow_avg,
                "body_shift": body_shift,
            },
        )


class LateralRaiseRule(FlyRule):
    pass


class FrontRaiseRule(FlyRule):
    pass


class ReverseFlyRule(FlyRule):
    pass


class PullRule(BaseRule):
    def check(self, keypoints, angles):
        if keypoints is None or angles is None:
            return self._no_pose()

        errors = []

        elbow_avg = self._elbow_avg(angles)
        shoulder_avg = self._shoulder_avg(angles)
        body_shift = self._body_shift(keypoints)
        torso_lean = torso_lean_from_vertical(keypoints)

        if elbow_avg is None:
            return self._no_pose()

        self._update_rep_low_to_high(
            elbow_avg,
            low_threshold=70,
            high_threshold=150,
        )

        if body_shift > 65:
            errors.append({"code": "too_much_torso_movement", "severity": "medium"})

        if shoulder_avg is not None and shoulder_avg > 160:
            errors.append({"code": "shoulder_shrug", "severity": "medium"})

        return self._result(
            errors,
            {
                "elbow_avg": elbow_avg,
                "shoulder_avg": shoulder_avg,
                "body_shift": body_shift,
                "torso_lean": torso_lean,
            },
        )


class RowRule(PullRule):
    def check(self, keypoints, angles):
        result = super().check(keypoints, angles)

        torso_lean = result["metrics"].get("torso_lean")
        if torso_lean is not None and torso_lean < 20:
            result["errors"].append({"code": "too_upright_for_row", "severity": "medium"})

        result["score"] = calculate_score(result["errors"])
        return result


class PulldownRule(PullRule):
    pass


class PullupRule(PullRule):
    pass


class PulloverRule(BaseRule):
    def check(self, keypoints, angles):
        if keypoints is None or angles is None:
            return self._no_pose()

        errors = []

        shoulder_avg = self._shoulder_avg(angles)
        elbow_avg = self._elbow_avg(angles)
        body_shift = self._body_shift(keypoints)

        if shoulder_avg is None:
            return self._no_pose()

        self._update_rep_high_to_low(
            shoulder_avg,
            low_threshold=40,
            high_threshold=130,
        )

        if elbow_avg is not None and elbow_avg < 140:
            errors.append({"code": "elbow_moving_too_much", "severity": "medium"})

        if body_shift > 60:
            errors.append({"code": "body_swing", "severity": "medium"})

        return self._result(
            errors,
            {
                "shoulder_avg": shoulder_avg,
                "elbow_avg": elbow_avg,
                "body_shift": body_shift,
            },
        )


class FacepullRule(PullRule):
    pass


class UprightRowRule(PullRule):
    pass


class DipRule(BaseRule):
    def check(self, keypoints, angles):
        if keypoints is None or angles is None:
            return self._no_pose()

        errors = []

        elbow_avg = self._elbow_avg(angles)
        torso_lean = torso_lean_from_vertical(keypoints)
        body_shift = self._body_shift(keypoints)

        if elbow_avg is None:
            return self._no_pose()

        self._update_rep_low_to_high(
            elbow_avg,
            low_threshold=80,
            high_threshold=155,
        )

        if body_shift > 65:
            errors.append({"code": "body_swing", "severity": "medium"})

        if elbow_avg < 55:
            errors.append({"code": "not_full_rom", "severity": "low"})

        return self._result(
            errors,
            {
                "elbow_avg": elbow_avg,
                "torso_lean": torso_lean,
                "body_shift": body_shift,
            },
        )


class LegPressRule(BaseRule):
    def check(self, keypoints, angles):
        if keypoints is None or angles is None:
            return self._no_pose()

        errors = [{"code": "limited_camera_check", "severity": "low"}]

        knee_avg = self._knee_avg(angles)
        hip_avg = self._hip_avg(angles)

        if knee_avg is None:
            return self._no_pose()

        self._update_rep_low_to_high(
            knee_avg,
            low_threshold=85,
            high_threshold=160,
        )

        if knee_avg > 172:
            errors.append({"code": "elbow_locked_hard", "severity": "low"})

        return self._result(
            errors,
            {
                "knee_avg": knee_avg,
                "hip_avg": hip_avg,
            },
        )


class LegCurlRule(BaseRule):
    def check(self, keypoints, angles):
        if keypoints is None or angles is None:
            return self._no_pose()

        errors = [{"code": "limited_camera_check", "severity": "low"}]

        knee_avg = self._knee_avg(angles)
        body_shift = self._body_shift(keypoints)

        if knee_avg is None:
            return self._no_pose()

        self._update_rep_low_to_high(
            knee_avg,
            low_threshold=70,
            high_threshold=155,
        )

        if body_shift > 60:
            errors.append({"code": "body_swing", "severity": "medium"})

        return self._result(
            errors,
            {
                "knee_avg": knee_avg,
                "body_shift": body_shift,
            },
        )


class LegExtensionRule(BaseRule):
    def check(self, keypoints, angles):
        if keypoints is None or angles is None:
            return self._no_pose()

        errors = [{"code": "limited_camera_check", "severity": "low"}]

        knee_avg = self._knee_avg(angles)
        body_shift = self._body_shift(keypoints)

        if knee_avg is None:
            return self._no_pose()

        self._update_rep_low_to_high(
            knee_avg,
            low_threshold=90,
            high_threshold=160,
        )

        if knee_avg > 172:
            errors.append({"code": "elbow_locked_hard", "severity": "low"})

        if body_shift > 60:
            errors.append({"code": "body_swing", "severity": "medium"})

        return self._result(
            errors,
            {
                "knee_avg": knee_avg,
                "body_shift": body_shift,
            },
        )


class CalfRaiseRule(BaseRule):
    def check(self, keypoints, angles):
        if keypoints is None or angles is None:
            return self._no_pose()

        errors = [{"code": "limited_camera_check", "severity": "low"}]

        body_shift = self._body_shift(keypoints)
        hip_diff = hip_balance_diff(keypoints)

        # MediaPipe không đo tốt cổ chân/calf raise từ laptop camera,
        # nên tạm dùng body_shift để phát hiện nhún người quá nhiều.
        if body_shift > 55:
            errors.append({"code": "heel_or_calf_bounce", "severity": "medium"})

        if hip_diff is not None and hip_diff > 35:
            errors.append({"code": "leg_imbalance", "severity": "low"})

        # Không có rep count chính xác cho calf nếu camera không thấy bàn chân rõ.
        self.stage = "calf_raise_check"

        return self._result(
            errors,
            {
                "body_shift": body_shift,
                "hip_diff": hip_diff,
            },
        )


class CrunchRule(BaseRule):
    def check(self, keypoints, angles):
        if keypoints is None or angles is None:
            return self._no_pose()

        errors = []

        torso_lean = torso_lean_from_vertical(keypoints)
        hip_avg = self._hip_avg(angles)
        body_shift = self._body_shift(keypoints)

        if torso_lean is None:
            return self._no_pose()

        self._update_rep_high_to_low(
            torso_lean,
            low_threshold=10,
            high_threshold=35,
        )

        if body_shift > 70:
            errors.append({"code": "using_back_instead_abs", "severity": "medium"})

        return self._result(
            errors,
            {
                "torso_lean": torso_lean,
                "hip_avg": hip_avg,
                "body_shift": body_shift,
            },
        )


class LegRaiseRule(BaseRule):
    def check(self, keypoints, angles):
        if keypoints is None or angles is None:
            return self._no_pose()

        errors = []

        hip_avg = self._hip_avg(angles)
        body_shift = self._body_shift(keypoints)

        if hip_avg is None:
            return self._no_pose()

        self._update_rep_high_to_low(
            hip_avg,
            low_threshold=70,
            high_threshold=140,
        )

        if body_shift > 70:
            errors.append({"code": "body_swing", "severity": "medium"})

        return self._result(
            errors,
            {
                "hip_avg": hip_avg,
                "body_shift": body_shift,
            },
        )


class TwistRule(BaseRule):
    def check(self, keypoints, angles):
        if keypoints is None or angles is None:
            return self._no_pose()

        errors = []

        shoulder_diff = shoulder_balance_diff(keypoints)
        hip_diff = hip_balance_diff(keypoints)
        body_shift = self._body_shift(keypoints)

        # Twist khó đếm rep bằng 2D pose nếu không có tracking rotation chuẩn.
        self.stage = "twist"

        if body_shift > 80:
            errors.append({"code": "twisting_too_fast", "severity": "medium"})

        return self._result(
            errors,
            {
                "shoulder_diff": shoulder_diff,
                "hip_diff": hip_diff,
                "body_shift": body_shift,
            },
        )


class SideBendRule(BaseRule):
    def check(self, keypoints, angles):
        if keypoints is None or angles is None:
            return self._no_pose()

        errors = []

        shoulder_diff = shoulder_balance_diff(keypoints)
        hip_diff = hip_balance_diff(keypoints)
        body_shift = self._body_shift(keypoints)

        self.stage = "side_bend"

        if body_shift > 80:
            errors.append({"code": "body_swing", "severity": "medium"})

        return self._result(
            errors,
            {
                "shoulder_diff": shoulder_diff,
                "hip_diff": hip_diff,
                "body_shift": body_shift,
            },
        )


class CoreDynamicRule(LegRaiseRule):
    pass


RULE_CLASS_MAP = {
    "squat": SquatRule,
    "hinge": HingeRule,
    "deadlift": DeadliftRule,

    "curl": CurlRule,
    "triceps_extension": TricepsExtensionRule,

    "press": PressRule,
    "shoulder_press": ShoulderPressRule,
    "fly": FlyRule,
    "dip": DipRule,

    "pulldown": PulldownRule,
    "pullup": PullupRule,
    "row": RowRule,
    "pullover": PulloverRule,
    "facepull": FacepullRule,
    "upright_row": UprightRowRule,

    "lateral_raise": LateralRaiseRule,
    "front_raise": FrontRaiseRule,
    "reverse_fly": ReverseFlyRule,

    "leg_press": LegPressRule,
    "leg_curl": LegCurlRule,
    "leg_extension": LegExtensionRule,
    "calf_raise": CalfRaiseRule,

    "crunch": CrunchRule,
    "leg_raise": LegRaiseRule,
    "twist": TwistRule,
    "side_bend": SideBendRule,
    "core_dynamic": CoreDynamicRule,
}


def create_rule_checker(exercise_slug, exercise_config):
    rule_name = exercise_config.get("rule")
    cls = RULE_CLASS_MAP.get(rule_name)

    if cls is None:
        raise ValueError(f"Unsupported rule type: {rule_name}")

    return cls(exercise=exercise_slug, config=exercise_config)
