import math

class PostureAnalyzer:
    def __init__(self):
        pass

    def _calculate_distance(self, p1, p2):
        if not p1 or not p2:
            return 0.0
        # Trả về công thức 2D chuẩn xác và ổn định
        return math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)

    def analyze_shape(self, landmarks, segmentation_mask=None):
        if not landmarks:
            return {"body_type": "Khong xac dinh", "description": "Chua bat duoc khung xuong."}

        # Trích xuất dữ liệu
        l_shoulder = landmarks.get('left_shoulder')
        r_shoulder = landmarks.get('right_shoulder')
        l_hip = landmarks.get('left_hip')
        r_hip = landmarks.get('right_hip')
        l_knee = landmarks.get('left_knee')
        r_knee = landmarks.get('right_knee')

        if not all([l_shoulder, r_shoulder, l_hip, r_hip]):
            return {"body_type": "Dang phan tich...", "description": ""}

        # --- CƠ CHẾ AN TOÀN (CHỐNG LỖI ĐỨNG QUÁ GẦN) ---
        # Kiểm tra xem có thấy đầu gối không (nghĩa là đứng đủ xa)
        # visibility > 0.5 nghĩa là bộ phận đó nằm rõ ràng trong camera
        if not l_knee or not r_knee or l_knee['visibility'] < 0.5 or r_knee['visibility'] < 0.5:
             return {
                 "body_type": "Chua the do dang", 
                 "description": "Vui long lui xa camera de thay toi dau goi!"
             }
        # -----------------------------------------------

        # 1. Đo tỷ lệ Khung xương
        shoulder_width = self._calculate_distance(l_shoulder, r_shoulder)
        hip_width = self._calculate_distance(l_hip, r_hip)
        
        if hip_width == 0:
            return {"body_type": "Dang phan tich...", "description": ""}
            
        ratio = shoulder_width / hip_width
        result = {"body_type": "", "description": ""}

        # Xác định hình dáng bộ xương cơ bản
        if ratio > 1.25:
            base_shape = "Dang chu V"
        elif 0.95 <= ratio <= 1.25:
            base_shape = "Dang chu nhat"
        else:
            base_shape = "Dang qua le"

        # 2. Đo độ Gầy, Béo, Vừa (Hoàn toàn bằng 2D chuẩn)
        mid_shoulder_y = (l_shoulder['y'] + r_shoulder['y']) / 2.0
        mid_hip_y = (l_hip['y'] + r_hip['y']) / 2.0
        back_length = abs(mid_hip_y - mid_shoulder_y)

        frame_thickness = shoulder_width / back_length if back_length > 0 else 0

        if frame_thickness < 0.65: 
            condition = "GAY (Thieu can)"
        elif frame_thickness > 0.85:
            condition = "BEO (Thua can)"
        else:
            condition = "VUA (Can doi)"

        # Gộp kết quả
        result["body_type"] = f"{base_shape} | {condition}"
        result["description"] = f"Ty le Vai/Lung: {round(frame_thickness, 2)}"
        
        return result