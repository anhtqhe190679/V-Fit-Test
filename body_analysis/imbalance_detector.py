import math

class ImbalanceDetector:
    def __init__(self, tilt_threshold=8.0):
        # Thiết lập ngưỡng dung sai 8 độ. Vượt quá góc này mới cảnh báo lệch vai/hông.
        self.threshold = tilt_threshold

    def _calculate_absolute_angle(self, p1, p2):
        """
        Tính góc nghiêng tuyệt đối (luôn dương từ 0 -> 90 độ).
        Loại bỏ hoàn toàn lỗi lật ngược góc do camera lật gương (flip).
        """
        if not p1 or not p2:
            return 0.0

        dx = abs(p2['x'] - p1['x'])
        dy = abs(p2['y'] - p1['y'])
        
        if dx == 0:  # Tránh lỗi chia cho 0 nếu cơ thể nằm dọc hoàn hảo
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

        # 1. Kiểm tra nghiêng vai (Trục Y)
        if l_shoulder and r_shoulder:
            shoulder_angle = self._calculate_absolute_angle(l_shoulder, r_shoulder)
            if shoulder_angle > self.threshold:
                # Trục Y hướng xuống: Tọa độ Y lớn hơn nghĩa là điểm đó nằm thấp hơn
                direction = "phai" if l_shoulder['y'] > r_shoulder['y'] else "trai"
                issues.append(f"Nghieng vai {direction} (Goc: {round(shoulder_angle, 1)} do)")

        # 2. Kiểm tra nghiêng hông (Trục Y)
        if l_hip and r_hip:
            hip_angle = self._calculate_absolute_angle(l_hip, r_hip)
            if hip_angle > self.threshold:
                direction = "phai" if l_hip['y'] > r_hip['y'] else "trai"
                issues.append(f"Nghieng hong {direction} (Goc: {round(hip_angle, 1)} do)")

        # 3. Kiểm tra nghiêng đầu / lệch cổ (Hệ quy chiếu động chuẩn tỉ lệ)
        if nose and l_shoulder and r_shoulder:
            mid_shoulder_x = (l_shoulder['x'] + r_shoulder['x']) / 2.0
            head_deviation = nose['x'] - mid_shoulder_x
            
            # Lấy bề ngang vai thực tế làm thước đo chuẩn động
            shoulder_width = abs(r_shoulder['x'] - l_shoulder['x'])
            
            if shoulder_width > 0:
                deviation_ratio = abs(head_deviation) / shoulder_width
                # Đầu phải lệch quá 15% bề ngang vai mới báo lỗi (Tránh việc để thẳng vẫn báo nghiêng)
                if deviation_ratio > 0.15:
                    direction = "trai" if head_deviation > 0 else "phai"
                    issues.append(f"Dau nghieng sang {direction}")

        return issues