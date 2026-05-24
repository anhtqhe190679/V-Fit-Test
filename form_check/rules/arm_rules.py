from form_check.rules.rule_utils import (
    avg_valid,
    point,
    distance,
    shoulder_hip_shift,
    calculate_score,
)


class BicepCurlRules:
    def __init__(
        self,
        up_threshold=55,
        down_threshold=155,
        elbow_move_threshold=45,
        body_swing_threshold=45,
    ):
        self.up_threshold = up_threshold
        self.down_threshold = down_threshold
        self.elbow_move_threshold = elbow_move_threshold
        self.body_swing_threshold = body_swing_threshold

        self.rep_count = 0
        self.stage = "down"
        self.was_up = False

        self.initial_left_elbow = None
        self.initial_right_elbow = None

    def reset(self):
        self.rep_count = 0
        self.stage = "down"
        self.was_up = False
        self.initial_left_elbow = None
        self.initial_right_elbow = None

    def check(self, keypoints, angles):
        errors = []

        if keypoints is None or angles is None:
            return self._result([{"code": "no_pose", "severity": "high"}], {})

        left_elbow_angle = angles.get("left_elbow")
        right_elbow_angle = angles.get("right_elbow")
        elbow_avg = avg_valid([left_elbow_angle, right_elbow_angle])

        if elbow_avg is None:
            return self._result([{"code": "no_pose", "severity": "high"}], {})

        left_elbow = point(keypoints, "left_elbow")
        right_elbow = point(keypoints, "right_elbow")

        if self.initial_left_elbow is None and left_elbow is not None:
            self.initial_left_elbow = left_elbow

        if self.initial_right_elbow is None and right_elbow is not None:
            self.initial_right_elbow = right_elbow

        # Rep counting
        if elbow_avg < self.up_threshold:
            self.stage = "up"
            self.was_up = True

        elif elbow_avg > self.down_threshold:
            if self.was_up:
                self.rep_count += 1
            self.stage = "down"
            self.was_up = False

        else:
            self.stage = "middle"

        # Khuỷu di chuyển quá nhiều
        left_move = distance(left_elbow, self.initial_left_elbow)
        right_move = distance(right_elbow, self.initial_right_elbow)

        move_values = [v for v in [left_move, right_move] if v is not None]
        elbow_move = max(move_values) if move_values else 0

        if elbow_move > self.elbow_move_threshold:
            errors.append({"code": "elbow_moving_too_much", "severity": "medium"})

        # Vung người
        body_shift = shoulder_hip_shift(keypoints)
        if body_shift is not None and body_shift > self.body_swing_threshold:
            errors.append({"code": "body_swing", "severity": "medium"})

        # ROM không đủ
        if self.stage == "middle" and self.rep_count == 0:
            if 80 < elbow_avg < 130:
                errors.append({"code": "not_full_rom", "severity": "low"})

        metrics = {
            "left_elbow": left_elbow_angle,
            "right_elbow": right_elbow_angle,
            "elbow_avg": elbow_avg,
            "elbow_move": elbow_move,
            "body_shift": body_shift,
        }

        return self._result(errors, metrics)

    def _result(self, errors, metrics):
        return {
            "exercise": "bicep_curl",
            "rep_count": self.rep_count,
            "stage": self.stage,
            "errors": errors,
            "metrics": metrics,
            "score": calculate_score(errors),
        }


class TricepsPushdownRules:
    def __init__(
        self,
        down_threshold=160,
        up_threshold=80,
        elbow_move_threshold=45,
        body_swing_threshold=45,
    ):
        self.down_threshold = down_threshold
        self.up_threshold = up_threshold
        self.elbow_move_threshold = elbow_move_threshold
        self.body_swing_threshold = body_swing_threshold

        self.rep_count = 0
        self.stage = "up"
        self.was_down = False

        self.initial_left_elbow = None
        self.initial_right_elbow = None

    def reset(self):
        self.rep_count = 0
        self.stage = "up"
        self.was_down = False
        self.initial_left_elbow = None
        self.initial_right_elbow = None

    def check(self, keypoints, angles):
        errors = []

        if keypoints is None or angles is None:
            return self._result([{"code": "no_pose", "severity": "high"}], {})

        left_elbow_angle = angles.get("left_elbow")
        right_elbow_angle = angles.get("right_elbow")
        elbow_avg = avg_valid([left_elbow_angle, right_elbow_angle])

        if elbow_avg is None:
            return self._result([{"code": "no_pose", "severity": "high"}], {})

        left_elbow = point(keypoints, "left_elbow")
        right_elbow = point(keypoints, "right_elbow")

        if self.initial_left_elbow is None and left_elbow is not None:
            self.initial_left_elbow = left_elbow

        if self.initial_right_elbow is None and right_elbow is not None:
            self.initial_right_elbow = right_elbow

        # Rep counting: tay duỗi xuống = elbow angle lớn
        if elbow_avg > self.down_threshold:
            self.stage = "down"
            self.was_down = True

        elif elbow_avg < self.up_threshold:
            if self.was_down:
                self.rep_count += 1
            self.stage = "up"
            self.was_down = False

        else:
            self.stage = "middle"

        # Khuỷu phải cố định
        left_move = distance(left_elbow, self.initial_left_elbow)
        right_move = distance(right_elbow, self.initial_right_elbow)

        move_values = [v for v in [left_move, right_move] if v is not None]
        elbow_move = max(move_values) if move_values else 0

        if elbow_move > self.elbow_move_threshold:
            errors.append({"code": "elbow_moving_too_much", "severity": "medium"})

        # Không vung người / dùng vai
        body_shift = shoulder_hip_shift(keypoints)
        if body_shift is not None and body_shift > self.body_swing_threshold:
            errors.append({"code": "body_swing", "severity": "medium"})

        metrics = {
            "left_elbow": left_elbow_angle,
            "right_elbow": right_elbow_angle,
            "elbow_avg": elbow_avg,
            "elbow_move": elbow_move,
            "body_shift": body_shift,
        }

        return self._result(errors, metrics)

    def _result(self, errors, metrics):
        return {
            "exercise": "triceps_pushdown",
            "rep_count": self.rep_count,
            "stage": self.stage,
            "errors": errors,
            "metrics": metrics,
            "score": calculate_score(errors),
        }
