import math
import numpy as np

class PostureAnalyzer:
    def __init__(self):
        pass

    def _calculate_distance(self, p1, p2):
        # Tính khoảng cách hình học chuẩn (Euclidean)
        return math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)

    def analyze_shape(self, landmarks, segmentation_mask=None):
        # 1. Đo tỷ lệ khung xương cơ bản để xác định Dáng (Shape)
        shoulder_width = self._calculate_distance(landmarks['left_shoulder'], landmarks['right_shoulder'])
        hip_width = self._calculate_distance(landmarks['left_hip'], landmarks['right_hip'])
        
        ratio = shoulder_width / hip_width if hip_width > 0 else 0
        
        # Đánh giá Dáng người (Shape)
        body_type = "Chua xac dinh"
        if ratio > 1.3:
            body_type = "Dang chu V (Vai rong)"
        elif 0.95 <= ratio <= 1.3:
            body_type = "Dang chu nhat"
        else:
            body_type = "Dang qua le (Hong to)"

        # ---------------------------------------------------------
        # 2. ĐO ĐỘ BÉO/GẦY BẰNG MẶT NẠ (KHÔNG PHỤ THUỘC KHOẢNG CÁCH)
        # ---------------------------------------------------------
        condition = "Chua ro (Thieu Mask)"
        
        if segmentation_mask is not None:
            # Lấy kích thước mặt nạ thực tế
            height, width = segmentation_mask.shape
            
            # Tìm tọa độ Y của Eo (Eo thường nằm ở 60% chiều dài từ Vai xuống Hông)
            mid_shoulder_y = (landmarks['left_shoulder']['y'] + landmarks['right_shoulder']['y']) / 2.0
            mid_hip_y = (landmarks['left_hip']['y'] + landmarks['right_hip']['y']) / 2.0
            waist_y_norm = mid_shoulder_y + (mid_hip_y - mid_shoulder_y) * 0.6
            
            # Chuyển đổi tọa độ Eo sang Pixel
            waist_y_px = int(waist_y_norm * height)
            
            # Trích xuất lát cắt ngang (slice) tại eo để đếm da thịt
            if 0 <= waist_y_px < height:
                waist_slice = segmentation_mask[waist_y_px, :]
                
                # Đếm bề ngang eo thực tế (da thịt) tính bằng pixel
                # Mask của mediapipe trả về giá trị từ 0.0 đến 1.0 (1.0 là người)
                waist_thickness_px = np.sum(waist_slice > 0.1)
                
                # Quy đổi bề ngang XƯƠNG VAI sang pixel để làm "Thước đo động"
                shoulder_width_px = shoulder_width * width
                
                # TÍNH TỶ LỆ (Bề ngang Eo mỡ / Bề ngang Xương vai)
                if shoulder_width_px > 0:
                    fat_ratio = waist_thickness_px / shoulder_width_px
                    
                    # Phân loại độ béo gầy dựa trên thể trạng thực tế
                    if fat_ratio < 0.85:
                        condition = "GAY (Thieu can)"
                    elif fat_ratio > 1.15:
                        condition = "BEO (Thua can)"
                    else:
                        condition = "VUA (Can doi)"

        return {
            "shoulder_hip_ratio": round(ratio, 2),
            "body_type": body_type,
            "description": condition
        }