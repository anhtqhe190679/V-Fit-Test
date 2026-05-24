# form_check/feedback_generator.py

FEEDBACK_DATABASE = {
    "no_pose": {
        "warning": "Không phát hiện được cơ thể.",
        "correction": "Hãy đứng sao cho toàn thân nằm trong khung hình camera.",
        "severity": "high",
    },

    "good_form": {
        "warning": "Form tốt.",
        "correction": "Tiếp tục giữ nhịp độ và kiểm soát động tác.",
        "severity": "low",
    },

    "limited_camera_check": {
        "warning": "Bài này chỉ được kiểm tra cơ bản bằng laptop camera.",
        "correction": "Hãy đặt camera sao cho thấy rõ khớp chính của bài tập.",
        "severity": "low",
    },

    # Lower body
    "not_deep_enough": {
        "warning": "Biên độ xuống chưa đủ.",
        "correction": "Hạ người sâu hơn nhưng vẫn giữ form an toàn.",
        "severity": "medium",
    },
    "knee_inward": {
        "warning": "Gối đang chụm vào trong.",
        "correction": "Đẩy gối ra ngoài, giữ gối đi cùng hướng với mũi chân.",
        "severity": "high",
    },
    "leg_imbalance": {
        "warning": "Hai chân di chuyển không đều.",
        "correction": "Dồn lực đều hai chân và kiểm soát nhịp đi xuống/đi lên.",
        "severity": "medium",
    },
    "back_leaning_too_much": {
        "warning": "Thân người nghiêng quá nhiều.",
        "correction": "Mở ngực, gồng core và giữ lưng ổn định hơn.",
        "severity": "medium",
    },
    "too_much_knee_bend": {
        "warning": "Gối gập quá nhiều so với yêu cầu bài này.",
        "correction": "Đẩy hông ra sau nhiều hơn, không biến động tác thành squat.",
        "severity": "medium",
    },
    "rounded_back": {
        "warning": "Lưng có dấu hiệu bị cong.",
        "correction": "Gồng bụng, giữ cột sống neutral và giảm biên độ nếu mất form.",
        "severity": "high",
    },
    "heel_or_calf_bounce": {
        "warning": "Có dấu hiệu nhún/bật người quá nhiều.",
        "correction": "Tập chậm lại, hạ gót có kiểm soát và nhón lên bằng bắp chuối.",
        "severity": "medium",
    },

    # Arm
    "body_swing": {
        "warning": "Bạn đang vung người.",
        "correction": "Giảm tạ, giữ thân người cố định và tập chậm lại.",
        "severity": "medium",
    },
    "elbow_moving_too_much": {
        "warning": "Khuỷu tay di chuyển quá nhiều.",
        "correction": "Giữ khuỷu ổn định, chỉ để cẳng tay di chuyển theo bài tập.",
        "severity": "medium",
    },
    "not_full_rom": {
        "warning": "Biên độ chuyển động chưa đủ.",
        "correction": "Đi hết ROM an toàn, không làm nửa reps quá nhiều.",
        "severity": "low",
    },
    "shoulder_compensation": {
        "warning": "Bạn đang dùng vai/người để hỗ trợ quá nhiều.",
        "correction": "Hạ vai xuống, giữ vai ổn định và dùng đúng nhóm cơ chính.",
        "severity": "medium",
    },
    "elbow_locked_hard": {
        "warning": "Có thể đang khóa khớp quá mạnh ở cuối rep.",
        "correction": "Duỗi gần thẳng nhưng không khóa cứng khớp.",
        "severity": "low",
    },

    # Press / fly / back / shoulder
    "elbow_flare_too_wide": {
        "warning": "Khuỷu có thể đang mở quá rộng.",
        "correction": "Giữ khuỷu ở góc vừa phải, không flare 90 độ hoàn toàn.",
        "severity": "medium",
    },
    "shoulder_shrug": {
        "warning": "Vai đang nhún lên quá nhiều.",
        "correction": "Hạ vai xuống, giữ cổ dài và kiểm soát chuyển động.",
        "severity": "medium",
    },
    "too_much_torso_movement": {
        "warning": "Thân người di chuyển quá nhiều.",
        "correction": "Gồng core, giữ thân ổn định và giảm tạ nếu cần.",
        "severity": "medium",
    },
    "pulling_with_arms": {
        "warning": "Có thể đang kéo bằng tay quá nhiều.",
        "correction": "Nghĩ đến kéo khuỷu về sau/xuống và siết lưng ở cuối rep.",
        "severity": "medium",
    },
    "too_upright_for_row": {
        "warning": "Bạn đang đứng quá thẳng khi row.",
        "correction": "Gập người khoảng 30–45 độ và giữ lưng neutral.",
        "severity": "medium",
    },

    # Core
    "using_back_instead_abs": {
        "warning": "Có thể đang dùng lưng/quán tính thay vì cơ bụng.",
        "correction": "Gập bằng cơ bụng, làm chậm và kiểm soát từng rep.",
        "severity": "medium",
    },
    "twisting_too_fast": {
        "warning": "Xoay người quá nhanh.",
        "correction": "Xoay chậm, kiểm soát thân người và siết bụng bên hông.",
        "severity": "medium",
    },
}


def generate_feedback(errors):
    if not errors:
        return [
            {
                "code": "good_form",
                **FEEDBACK_DATABASE["good_form"],
            }
        ]

    feedback = []

    for error in errors:
        code = error["code"] if isinstance(error, dict) else str(error)

        item = FEEDBACK_DATABASE.get(
            code,
            {
                "warning": code,
                "correction": "Kiểm tra lại form tập.",
                "severity": "medium",
            },
        )

        severity = error.get("severity", item["severity"]) if isinstance(error, dict) else item["severity"]

        feedback.append(
            {
                "code": code,
                "warning": item["warning"],
                "correction": item["correction"],
                "severity": severity,
            }
        )

    return feedback
