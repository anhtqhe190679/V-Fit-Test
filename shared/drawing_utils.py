import cv2
import mediapipe as mp
import numpy as np
import textwrap
from PIL import Image, ImageDraw, ImageFont


mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


# ============================================================
# Font utilities for Vietnamese text
# cv2.putText does NOT support Vietnamese Unicode.
# So we use Pillow for warning / correction text.
# ============================================================

_FONT_CACHE = {}


def get_vietnamese_font(size=24, bold=False):
    """
    Load a font that supports Vietnamese.
    Works well on Ubuntu if DejaVu/Noto fonts are installed.
    """

    cache_key = (size, bold)
    if cache_key in _FONT_CACHE:
        return _FONT_CACHE[cache_key]

    if bold:
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        ]
    else:
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]

    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, size)
            _FONT_CACHE[cache_key] = font
            return font
        except OSError:
            continue

    # Fallback, but may not display Vietnamese correctly
    font = ImageFont.load_default()
    _FONT_CACHE[cache_key] = font
    return font


def draw_unicode_text(
    frame,
    text,
    position,
    font_size=24,
    color=(255, 255, 255),
    bold=False,
):
    """
    Draw Vietnamese Unicode text on OpenCV frame using Pillow.

    Args:
        frame: OpenCV BGR image
        text: text to draw
        position: (x, y)
        font_size: font size
        color: BGR color, same style as OpenCV
        bold: use bold font
    """

    if text is None:
        return

    x, y = position

    # OpenCV BGR -> PIL RGB
    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)

    font = get_vietnamese_font(size=font_size, bold=bold)

    # BGR -> RGB
    rgb_color = (color[2], color[1], color[0])

    draw.text((x, y), str(text), font=font, fill=rgb_color)

    # PIL RGB -> OpenCV BGR
    frame[:, :, :] = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)


def draw_wrapped_unicode_text(
    frame,
    text,
    position,
    font_size=22,
    color=(255, 255, 255),
    bold=False,
    max_chars=70,
    line_gap=30,
):
    """
    Draw long Vietnamese text with line wrapping.
    Returns the y position after the last line.
    """

    if text is None:
        return position[1]

    x, y = position
    lines = textwrap.wrap(str(text), width=max_chars)

    if not lines:
        return y

    for i, line in enumerate(lines):
        draw_unicode_text(
            frame,
            line,
            (x, y + i * line_gap),
            font_size=font_size,
            color=color,
            bold=bold,
        )

    return y + len(lines) * line_gap


# ============================================================
# Pose drawing
# ============================================================

def draw_pose_landmarks(frame, results):
    if results is None:
        return

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

        # Keypoint names are English, so cv2.putText is fine here.
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


# ============================================================
# Form-check result drawing
# ============================================================

def draw_form_result(frame, form_result):
    """
    Draw:
    - exercise name
    - rep count
    - stage
    - score
    - warning
    - correction

    This function supports Vietnamese text.
    """

    if form_result is None:
        return

    frame_height, frame_width = frame.shape[:2]

    x = 20
    y = 20

    panel_width = min(frame_width - 20, 920)
    panel_height = 250

    exercise = form_result.get("exercise", "unknown")
    rep_count = form_result.get("rep_count", 0)
    stage = form_result.get("stage", "unknown")
    score = form_result.get("score", 0)
    feedback = form_result.get("feedback", [])

    # Background panel
    cv2.rectangle(
        frame,
        (10, 10),
        (panel_width, panel_height),
        (0, 0, 0),
        -1,
    )

    # Exercise line
    draw_unicode_text(
        frame,
        f"Exercise: {exercise}",
        (x, y),
        font_size=26,
        color=(255, 255, 255),
        bold=True,
    )

    # Reps / stage / score
    draw_unicode_text(
        frame,
        f"Reps: {rep_count} | Stage: {stage} | Score: {score}",
        (x, y + 38),
        font_size=25,
        color=(0, 255, 255),
        bold=True,
    )

    if not feedback:
        return

    first = feedback[0]

    warning = first.get("warning", "")
    correction = first.get("correction", "")
    severity = first.get("severity", "low")

    # Severity color
    if severity == "high":
        warning_color = (0, 0, 255)       # Red in BGR
    elif severity == "medium":
        warning_color = (0, 255, 255)     # Yellow in BGR
    else:
        warning_color = (0, 255, 0)       # Green in BGR

    # Warning
    next_y = draw_wrapped_unicode_text(
        frame,
        f"CẢNH BÁO: {warning}",
        (x, y + 78),
        font_size=23,
        color=warning_color,
        bold=True,
        max_chars=65,
        line_gap=30,
    )

    # Correction
    next_y = draw_wrapped_unicode_text(
        frame,
        f"SỬA FORM: {correction}",
        (x, next_y + 8),
        font_size=21,
        color=(255, 255, 255),
        bold=False,
        max_chars=75,
        line_gap=28,
    )

    # Show second feedback if available
    if len(feedback) > 1 and next_y < panel_height - 30:
        second = feedback[1]
        second_correction = second.get("correction", "")

        draw_wrapped_unicode_text(
            frame,
            f"GỢI Ý TIẾP: {second_correction}",
            (x, next_y + 8),
            font_size=20,
            color=(255, 255, 255),
            bold=False,
            max_chars=75,
            line_gap=26,
        )
