import math

class ImbalanceDetector:
    # Set threshold mặc định là 5.0 độ. Lệch quá 5 độ là AI sẽ báo lỗi.
    def __init__(self, tilt_threshold=5.0):
        self.threshold = tilt_threshold

    def _calculate_absolute_angle(self, p1, p2):
        """Tính góc nghiêng tuyệt đối giữa 2 điểm"""
        if not p1 or not p2:
            return 0.0

        dx = abs(p2['x'] - p1['x'])
        dy = abs(p2['y'] - p1['y'])
        
        if dx == 0:
            return 90.0
            
        return math.degrees(math.atan(dy / dx))

    def detect_imbalance(self, landmarks):
        if not landmarks:
            return []

        issues = []
        
        l_shoulder = landmarks.get('left_shoulder')
        r_shoulder = landmarks.get('right_shoulder')
        l_hip = landmarks.get('left_hip')
        r_hip = landmarks.get('right_hip')
        nose = landmarks.get('nose')

        # 1. Kiểm tra nghiêng vai
        if l_shoulder and r_shoulder:
            shoulder_angle = self._calculate_absolute_angle(l_shoulder, r_shoulder)
            if shoulder_angle > self.threshold:
                direction = "phai" if l_shoulder['y'] > r_shoulder['y'] else "trai"
                issues.append(f"Nghieng vai {direction} ({round(shoulder_angle, 1)} do)")

        # 2. Kiểm tra nghiêng hông
        if l_hip and r_hip:
            hip_angle = self._calculate_absolute_angle(l_hip, r_hip)
            if hip_angle > self.threshold:
                direction = "phai" if l_hip['y'] > r_hip['y'] else "trai"
                issues.append(f"Nghieng hong {direction} ({round(hip_angle, 1)} do)")

        # 3. Kiểm tra nghiêng đầu / lệch cổ
        if nose and l_shoulder and r_shoulder:
            mid_shoulder_x = (l_shoulder['x'] + r_shoulder['x']) / 2.0
            head_deviation = nose['x'] - mid_shoulder_x
            shoulder_width = abs(r_shoulder['x'] - l_shoulder['x'])
            
            if shoulder_width > 0:
                deviation_ratio = abs(head_deviation) / shoulder_width
                if deviation_ratio > 0.15: # Đầu lệch khỏi tâm vai quá 15%
                    direction = "phai" if head_deviation > 0 else "trai"
                    issues.append(f"Dau lech sang {direction}")

        # 4. Kiểm tra nghiêng CẢ NGƯỜI (Trục cơ thể)
        if l_shoulder and r_shoulder and l_hip and r_hip:
            mid_shoulder_x = (l_shoulder['x'] + r_shoulder['x']) / 2.0
            mid_hip_x = (l_hip['x'] + r_hip['x']) / 2.0
            mid_shoulder_y = (l_shoulder['y'] + r_shoulder['y']) / 2.0
            mid_hip_y = (l_hip['y'] + r_hip['y']) / 2.0
            
            dy = abs(mid_shoulder_y - mid_hip_y)
            dx = abs(mid_shoulder_x - mid_hip_x)
            
            if dy > 0:
                body_tilt = math.degrees(math.atan(dx / dy)) # Góc so với trục dọc
                if body_tilt > self.threshold:
                    direction = "phai" if mid_shoulder_x > mid_hip_x else "trai"
                    issues.append(f"Nghieng ca nguoi {direction} ({round(body_tilt, 1)} do)")

        return issues