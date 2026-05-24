# form_check/exercise_registry.py

EXERCISES = [
    # =========================
    # TAY SAU
    # =========================
    {
        "slug": "triceps_pushdown",
        "display_name": "Triceps Pushdown",
        "rule": "triceps_extension",
        "view": "side",
    },
    {
        "slug": "lying_triceps_extension",
        "display_name": "Lying Triceps Extension",
        "rule": "triceps_extension",
        "view": "side",
    },
    {
        "slug": "overhead_triceps_extension",
        "display_name": "Overhead Triceps Extension",
        "rule": "triceps_extension",
        "view": "side",
    },

    # =========================
    # TAY TRƯỚC
    # =========================
    {
        "slug": "cable_bayesian_curl",
        "display_name": "Cable Bayesian Curl",
        "rule": "curl",
        "view": "side",
    },
    {
        "slug": "incline_dumbbell_curl",
        "display_name": "Incline Dumbbell Curl",
        "rule": "curl",
        "view": "side",
    },
    {
        "slug": "bicep_curl",
        "display_name": "Bicep Curl",
        "rule": "curl",
        "view": "side",
    },

    # =========================
    # CHÂN
    # =========================
    {
        "slug": "dumbbell_romanian_deadlift",
        "display_name": "Dumbbell Romanian Deadlift",
        "rule": "hinge",
        "view": "side",
    },
    {
        "slug": "romanian_deadlift",
        "display_name": "Romanian Deadlift",
        "rule": "hinge",
        "view": "side",
    },
    {
        "slug": "barbell_deadlift",
        "display_name": "Barbell Deadlift",
        "rule": "deadlift",
        "view": "side",
    },
    {
        "slug": "deadlift",
        "display_name": "Deadlift",
        "rule": "deadlift",
        "view": "side",
    },
    {
        "slug": "barbell_squat",
        "display_name": "Barbell Squat",
        "rule": "squat",
        "view": "side",
    },
    {
        "slug": "squat",
        "display_name": "Squat",
        "rule": "squat",
        "view": "side",
    },
    {
        "slug": "smith_squat",
        "display_name": "Smith Squat",
        "rule": "squat",
        "view": "side",
    },
    {
        "slug": "leg_press",
        "display_name": "Leg Press",
        "rule": "leg_press",
        "view": "side",
    },
    {
        "slug": "leg_curl",
        "display_name": "Leg Curl",
        "rule": "leg_curl",
        "view": "side",
    },
    {
        "slug": "leg_extension",
        "display_name": "Leg Extension",
        "rule": "leg_extension",
        "view": "side",
    },
    {
        "slug": "smith_machine_calf_raise",
        "display_name": "Smith Machine Calf Raise",
        "rule": "calf_raise",
        "view": "side",
    },

    # =========================
    # BỤNG / LIÊN SƯỜN
    # =========================
    {
        "slug": "cable_crunch",
        "display_name": "Cable Crunch",
        "rule": "crunch",
        "view": "side",
    },
    {
        "slug": "ab_crunch_machine",
        "display_name": "Ab Crunch Machine",
        "rule": "crunch",
        "view": "side",
    },
    {
        "slug": "hanging_leg_raise",
        "display_name": "Hanging Leg Raise",
        "rule": "leg_raise",
        "view": "front",
    },
    {
        "slug": "russian_twist",
        "display_name": "Russian Twist",
        "rule": "twist",
        "view": "front",
    },
    {
        "slug": "cable_wood_chop",
        "display_name": "Cable Wood Chop",
        "rule": "twist",
        "view": "front",
    },
    {
        "slug": "bicycle_crunch",
        "display_name": "Bicycle Crunch",
        "rule": "core_dynamic",
        "view": "front",
    },
    {
        "slug": "dumbbell_side_bend",
        "display_name": "Dumbbell Side Bend",
        "rule": "side_bend",
        "view": "front",
    },

    # =========================
    # NGỰC
    # =========================
    {
        "slug": "dumbbell_bench_press",
        "display_name": "Dumbbell Bench Press",
        "rule": "press",
        "view": "side",
    },
    {
        "slug": "barbell_bench_press",
        "display_name": "Barbell Bench Press",
        "rule": "press",
        "view": "side",
    },
    {
        "slug": "cable_chest_fly",
        "display_name": "Cable Chest Fly",
        "rule": "fly",
        "view": "front",
    },
    {
        "slug": "machine_chest_fly",
        "display_name": "Machine Chest Fly",
        "rule": "fly",
        "view": "front",
    },
    {
        "slug": "barbell_incline_bench_press",
        "display_name": "Barbell Incline Bench Press",
        "rule": "press",
        "view": "side",
    },
    {
        "slug": "dumbbell_incline_bench_press",
        "display_name": "Dumbbell Incline Bench Press",
        "rule": "press",
        "view": "side",
    },
    {
        "slug": "cable_low_chest_fly",
        "display_name": "Cable Low Chest Fly",
        "rule": "fly",
        "view": "front",
    },
    {
        "slug": "high_to_low_cable_fly",
        "display_name": "High To Low Cable Fly",
        "rule": "fly",
        "view": "front",
    },
    {
        "slug": "dip",
        "display_name": "Dip",
        "rule": "dip",
        "view": "side",
    },

    # =========================
    # LƯNG
    # =========================
    {
        "slug": "lat_pulldown",
        "display_name": "Lat Pulldown",
        "rule": "pulldown",
        "view": "front",
    },
    {
        "slug": "pull_up",
        "display_name": "Pull Up",
        "rule": "pullup",
        "view": "front",
    },
    {
        "slug": "dumbbell_row",
        "display_name": "Dumbbell Row",
        "rule": "row",
        "view": "side",
    },
    {
        "slug": "cable_straight_arm_lat_pullover",
        "display_name": "Cable Straight-Arm Lat Pullover",
        "rule": "pullover",
        "view": "side",
    },
    {
        "slug": "seated_cable_row",
        "display_name": "Seated Cable Row",
        "rule": "row",
        "view": "side",
    },
    {
        "slug": "barbell_row",
        "display_name": "Barbell Row",
        "rule": "row",
        "view": "side",
    },
    {
        "slug": "facepull",
        "display_name": "Facepull",
        "rule": "facepull",
        "view": "front",
    },

    # =========================
    # VAI
    # =========================
    {
        "slug": "machine_shoulder_press",
        "display_name": "Machine Shoulder Press",
        "rule": "shoulder_press",
        "view": "front",
    },
    {
        "slug": "arnold_dumbbell_shoulder_press",
        "display_name": "Arnold Dumbbell Shoulder Press",
        "rule": "shoulder_press",
        "view": "front",
    },
    {
        "slug": "dumbbell_shoulder_press",
        "display_name": "Dumbbell Shoulder Press",
        "rule": "shoulder_press",
        "view": "front",
    },
    {
        "slug": "cable_front_raise",
        "display_name": "Cable Front Raise",
        "rule": "front_raise",
        "view": "side",
    },
    {
        "slug": "dumbbell_lateral_raise",
        "display_name": "Dumbbell Lateral Raise",
        "rule": "lateral_raise",
        "view": "front",
    },
    {
        "slug": "cable_shoulder_raise",
        "display_name": "Cable Shoulder Raise",
        "rule": "lateral_raise",
        "view": "front",
    },
    {
        "slug": "barbell_upright_row",
        "display_name": "Barbell Upright Row",
        "rule": "upright_row",
        "view": "front",
    },
    {
        "slug": "reverse_fly",
        "display_name": "Reverse Fly",
        "rule": "reverse_fly",
        "view": "front",
    },
    {
        "slug": "dumbbell_one_arm_reverse_fly",
        "display_name": "Dumbbell One Arm Reverse Fly",
        "rule": "reverse_fly",
        "view": "front",
    },
    {
        "slug": "rear_delt_fly",
        "display_name": "Rear Delt Fly",
        "rule": "reverse_fly",
        "view": "front",
    },
]


EXERCISE_MAP = {item["slug"]: item for item in EXERCISES}
EXERCISE_SLUGS = [item["slug"] for item in EXERCISES]


def get_exercise_config(slug):
    return EXERCISE_MAP.get(slug)


def get_exercise_name(slug):
    config = get_exercise_config(slug)
    if config is None:
        return slug
    return config["display_name"]
