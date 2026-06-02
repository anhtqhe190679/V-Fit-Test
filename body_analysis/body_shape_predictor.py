# file: body_analysis/body_shape_predictor.py
import numpy as np
from ultralytics import YOLO

class BodyShapePredictor:
    def __init__(self, model_path="best.pt"):
        # Load mô hình YOLOv8-seg của bạn
        self.model = YOLO(model_path)

    def predict(self, frame, shoulder_width_px):
        """
        frame: Ảnh từ camera
        shoulder_width_px: Bề ngang khung vai (pixel) lấy từ MediaPipe
        """
        # Chạy YOLO Segmentation
        results = self.model(frame, verbose=False)
        
        if not results or not results[0].masks:
            return {
                "body_shape": "Chưa xác định", 
                "description": "Không tìm thấy mặt nạ cơ thể"
            }

        # Lấy mask (mặt nạ trắng đen) của người đầu tiên
        mask = results[0].masks.data[0].cpu().numpy()
        h, w = mask.shape
        
        # 1. Đo độ dày vùng bụng: Lấy lát cắt ngang ở vị trí 60% chiều cao cơ thể (vùng eo)
        waist_y = int(h * 0.60)
        waist_slice = mask[waist_y, :]
        
        # Đếm số pixel màu trắng (tức là độ dày da thịt ở bụng)
        waist_thickness_px = np.sum(waist_slice > 0.1)
        
        # Nếu không bắt được vai từ MediaPipe, tránh lỗi chia cho 0
        if not shoulder_width_px or shoulder_width_px <= 0:
            shoulder_width_px = w * 0.25 # Ước lượng tạm

        # 2. Tính tỷ lệ Vàng (Độ dày bụng / Bề ngang vai)
        # Tỷ lệ này không bị ảnh hưởng bởi việc bạn đứng xa hay gần camera
        fat_ratio = waist_thickness_px / shoulder_width_px
        
        # 3. Phân loại Béo/Gầy thuần túy bằng Computer Vision (Bỏ BMI)
        if fat_ratio < 0.75:
            shape = "GAY (Thieu co/mo)"
            desc = f"Eo/Vai: {fat_ratio:.2f}. Can tang can, tap Hypertrophy."
        elif 0.75 <= fat_ratio <= 0.85:
            shape = "CAN DOI (Dang chu V)"
            desc = f"Eo/Vai: {fat_ratio:.2f}. The hinh dep, ty le chuan."
        else:
            shape = "BEO (Thua mo)"
            desc = f"Eo/Vai: {fat_ratio:.2f}. Bung to hon vai, can giam mo."
            
        return {
            "body_shape": shape,
            "description": desc,
            "fat_ratio": fat_ratio
        }