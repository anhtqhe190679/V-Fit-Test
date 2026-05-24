# form_check/form_checker.py

from shared.angle_calculator import calculate_body_angles
from form_check.feedback_generator import generate_feedback
from form_check.exercise_registry import get_exercise_config
from form_check.rules.generic_rules import create_rule_checker


class FormChecker:
    def __init__(self, exercise="squat", camera_view=None):
        self.exercise = exercise
        self.camera_view = camera_view
        self.exercise_config = None
        self.rule_checker = None

        self.set_exercise(exercise)

    def set_exercise(self, exercise):
        config = get_exercise_config(exercise)

        if config is None:
            raise ValueError(f"Unsupported exercise: {exercise}")

        self.exercise = exercise
        self.exercise_config = dict(config)

        if self.camera_view is not None:
            self.exercise_config["view"] = self.camera_view

        self.rule_checker = create_rule_checker(
            exercise_slug=exercise,
            exercise_config=self.exercise_config,
        )

    def set_camera_view(self, camera_view):
        self.camera_view = camera_view
        self.set_exercise(self.exercise)

    def check(self, keypoints, angles=None):
        if keypoints is None:
            result = {
                "exercise": self.exercise,
                "rep_count": 0,
                "stage": "unknown",
                "errors": [{"code": "no_pose", "severity": "high"}],
                "metrics": {},
                "score": 0,
            }
            result["feedback"] = generate_feedback(result["errors"])
            return result

        if angles is None:
            angles = calculate_body_angles(keypoints)

        result = self.rule_checker.check(keypoints, angles)
        result["feedback"] = generate_feedback(result.get("errors", []))
        return result

    def reset(self):
        self.rule_checker.reset()
