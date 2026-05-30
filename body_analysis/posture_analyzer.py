import math
import numpy as np

class PostureAnalyzer:
    def __init__(self):
        pass

    def _calculate_distance(self, p1, p2):
        return math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)

    def analyze_shape(self, landmarks, segmentation_mask=None):
        # 1. Đo tỷ lệ khung xương (Các giá trị này ĐÃ LÀ PIXEL)
        shoulder_width = self._calculate_distance(landmarks['left_shoulder'], landmarks['right_shoulder'])
        hip_width = self._calculate_distance(landmarks['left_hip'], landmarks['right_hip'])
        
        ratio = shoulder_width / hip_width if hip_width > 0 else 0
        
        body_type = "Chua xac dinh"
        if ratio > 1.3:
            body_type = "Dang chu V (Vai rong)"
        elif 0.95 <= ratio <= 1.3:
            body_type = "Dang chu nhat"
        else:
            body_type = "Dang qua le (Hong to)"

        # ---------------------------------------------------------
        # 2. ĐO ĐỘ BÉO/GẦY BẰNG MẶT NẠ (ĐÃ SỬA HỆ TỌA ĐỘ VÀ LỌC CÁNH TAY)
        # ---------------------------------------------------------
        condition = "Chua ro (Thieu Mask)"
        
        if segmentation_mask is not None:
            height, width = segmentation_mask.shape
            
            # Tọa độ Y của eo đã là Pixel, KHÔNG nhân thêm height nữa!
            mid_shoulder_y = (landmarks['left_shoulder']['y'] + landmarks['right_shoulder']['y']) / 2.0
            mid_hip_y = (landmarks['left_hip']['y'] + landmarks['right_hip']['y']) / 2.0
            waist_y_px = int(mid_shoulder_y + (mid_hip_y - mid_shoulder_y) * 0.6)
            
            # Trích xuất lát cắt ngang (slice) tại eo
            if 0 <= waist_y_px < height:
                # TÌM GIỚI HẠN HAI BÊN SƯỜN (Loại bỏ 2 cánh tay thõng xuống)
                left_bound = int(min(landmarks['left_shoulder']['x'], landmarks['left_hip']['x']))
                right_bound = int(max(landmarks['right_shoulder']['x'], landmarks['right_hip']['x']))
                
                # Nới rộng lề ra 5% để không cắt lẹm vào da thịt
                margin = int(width * 0.05)
                left_bound = max(0, left_bound - margin)
                right_bound = min(width, right_bound + margin)
                
                # Chỉ cắt lát vùng eo thực sự, bỏ qua 2 bên rìa ngoài (cánh tay)
                waist_slice = segmentation_mask[waist_y_px, left_bound:right_bound]
                waist_thickness_px = np.sum(waist_slice > 0.1)
                
                # Bề ngang vai cũng đã là Pixel
                shoulder_width_px = shoulder_width 
                
                if shoulder_width_px > 0:
                    fat_ratio = waist_thickness_px / shoulder_width_px
                    
                    # Cập nhật lại mốc so sánh vì đã gọt bỏ cánh tay
                    if fat_ratio < 0.80:
                        condition = "GAY (Thieu can)"
                    elif fat_ratio > 1.05:
                        condition = "BEO (Thua can)"
                    else:
                        condition = "VUA (Can doi)"

        return {
            "shoulder_hip_ratio": round(ratio, 2),
            "body_type": body_type,
            "description": condition
        }