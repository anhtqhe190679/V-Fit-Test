import math

class PostureAnalyzer:
    def __init__(self):
        pass

    def _calculate_distance(self, p1, p2):
        if not p1 or not p2:
            return 0.0
        return math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)

    def analyze_shape(self, landmarks, segmentation_mask=None):
        if not landmarks:
            return {"body_type": "Khong xac dinh", "description": "Chua bat duoc khung xuong."}

        # Trích xuất dữ liệu an toàn
        l_shoulder = landmarks.get('left_shoulder')
        r_shoulder = landmarks.get('right_shoulder')
        l_hip = landmarks.get('left_hip')
        r_hip = landmarks.get('right_hip')

        if not all([l_shoulder, r_shoulder, l_hip, r_hip]):
            return {"body_type": "Dang phan tich...", "description": ""}

        # 1. Đo tỷ lệ Khung xương (Chỉ phán dáng, không phán gầy/béo ở đây)
        shoulder_width = self._calculate_distance(l_shoulder, r_shoulder)
        hip_width = self._calculate_distance(l_hip, r_hip)
        
        if hip_width == 0:
            return {"body_type": "Dang phan tich...", "description": ""}

        ratio = shoulder_width / hip_width
        
        result = {
            "body_type": "",
            "description": ""
        }

        # Xác định hình dáng bộ xương cơ bản
        if ratio > 1.25:
            result["body_type"] = "Dang chu V"
        elif 0.95 <= ratio <= 1.25:
            result["body_type"] = "Dang chu nhat"
        else:
            result["body_type"] = "Dang qua le"

        # 2. Nội suy Gầy/Béo qua tỷ lệ Khung thân (Nâng độ nhạy cho người gầy)
        mid_shoulder_y = (l_shoulder['y'] + r_shoulder['y']) / 2.0
        mid_hip_y = (l_hip['y'] + r_hip['y']) / 2.0
        back_length = abs(mid_hip_y - mid_shoulder_y)

        # Tính tỷ lệ: Bề ngang vai chia cho Chiều dài lưng
        frame_thickness = shoulder_width / back_length if back_length > 0 else 0

        # CẬP NHẬT NGƯỠNG CHUẨN MEDIA PIPE 2D:
        # Nâng ngưỡng gầy lên 0.66 (để bắt nhạy hơn cơ thể thiếu cơ/mỏng người)
        if frame_thickness < 0.66: 
            result["body_type"] += " - Thieu can (Gay)"
            result["description"] = "Khung xuong hep, khoi luong co/mo dang o muc thap. Can tang co."
        elif frame_thickness > 0.78: 
            result["body_type"] += " - Thua can (Beo)"
            result["description"] = "Ty le be ngang lon, co the dang thua mo hoac rat to."
        else:
            result["body_type"] += " - Can doi"
            result["description"] = "Ty le mo/co o muc tuong doi khoe manh."

        return result