FEEDBACK_DATABASE = {
    "no_pose": {
        "warning": "Không phát hiện được cơ thể.",
        "correction": "Hãy đứng sao cho toàn thân nằm trong khung hình camera.",
        "severity": "high",
    },

    # Squat
    "not_deep_enough": {
        "warning": "Squat chưa đủ sâu.",
        "correction": "Hạ người xuống đến khi đùi gần song song với sàn hoặc thấp hơn một chút.",
        "severity": "medium",
    },
    "knee_inward": {
        "warning": "Gối đang chụm vào trong.",
        "correction": "Đẩy gối ra ngoài, giữ gối đi cùng hướng với mũi chân.",
        "severity": "high",
    },
    "back_leaning_too_much": {
        "warning": "Bạn đang nghiêng người quá nhiều.",
        "correction": "Mở ngực, gồng core, giữ lưng neutral hơn.",
        "severity": "medium",
    },
    "leg_imbalance": {
        "warning": "Hai chân đang di chuyển không đều.",
        "correction": "Dồn lực đều hai chân và đẩy lên bằng midfoot.",
        "severity": "medium",
    },

    # RDL / Deadlift
    "rounded_back": {
        "warning": "Lưng có dấu hiệu bị cong.",
        "correction": "Gồng bụng, giữ lưng neutral và gập người bằng hông.",
        "severity": "high",
    },
    "squatting_instead_of_hinging": {
        "warning": "Bạn đang squat xuống thay vì hip hinge.",
        "correction": "Đẩy hông ra sau, chỉ chùng gối nhẹ, giữ tạ sát chân.",
        "severity": "medium",
    },
    "too_much_knee_bend": {
        "warning": "Gối đang gập quá nhiều.",
        "correction": "Với RDL, hãy đẩy hông ra sau thay vì ngồi xuống như squat.",
        "severity": "medium",
    },

    # Bicep curl / Triceps
    "body_swing": {
        "warning": "Bạn đang vung người.",
        "correction": "Giảm tạ, giữ thân người cố định và tập chậm lại.",
        "severity": "medium",
    },
    "elbow_moving_too_much": {
        "warning": "Khuỷu tay di chuyển quá nhiều.",
        "correction": "Giữ khuỷu gần thân người, chỉ để cẳng tay di chuyển.",
        "severity": "medium",
    },
    "shoulder_compensation": {
        "warning": "Bạn đang dùng vai để hỗ trợ động tác.",
        "correction": "Hạ vai xuống, cố định vai và dùng đúng nhóm cơ chính.",
        "severity": "medium",
    },
    "not_full_rom": {
        "warning": "Biên độ chuyển động chưa đủ.",
        "correction": "Duỗi và co tay có kiểm soát, đi hết ROM an toàn.",
        "severity": "low",
    },

    "good_form": {
        "warning": "Form tốt.",
        "correction": "Tiếp tục giữ nhịp độ và kiểm soát động tác.",
        "severity": "low",
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

        feedback.append(
            {
                "code": code,
                "warning": item["warning"],
                "correction": item["correction"],
                "severity": error.get("severity", item["severity"]) if isinstance(error, dict) else item["severity"],
            }
        )

    return feedback
