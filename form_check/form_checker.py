from shared.angle_calculator import calculate_body_angles
from form_check.feedback_generator import generate_feedback
from form_check.rules.squat_rules import SquatRules
from form_check.rules.leg_rules import RomanianDeadliftRules, DeadliftRules
from form_check.rules.arm_rules import BicepCurlRules, TricepsPushdownRules

class FormChecker:
    def __init__(self, exercise="squat", camera_view="side"):
        self.exercise = exercise
        self.camera_view = camera_view
        self.rule_checker = self._create_rule_checker(exercise)

    def _create_rule_checker(self, exercise):
        if exercise == "squat":
            return SquatRules(camera_view=self.camera_view)

        if exercise in ["romanian_deadlift", "rdl"]:
            return RomanianDeadliftRules()

        if exercise == "deadlift":
            return DeadliftRules()

        if exercise == "bicep_curl":
            return BicepCurlRules()

        if exercise == "triceps_pushdown":
            return TricepsPushdownRules()

        raise ValueError(f"Unsupported exercise: {exercise}")

    def set_exercise(self, exercise):
        self.exercise = exercise
        self.rule_checker = self._create_rule_checker(exercise)

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
