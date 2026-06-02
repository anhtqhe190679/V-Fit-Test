# file: body_analysis/body_analyzer.py
import math
from body_analysis.body_shape_predictor import BodyShapePredictor
# Nếu có ImbalanceDetector thì bạn cứ import và để lại bình thường
# from body_analysis.imbalance_detector import ImbalanceDetector

class BodyAnalyzer:
    def __init__(self):
        # Khởi tạo mô hình AI nhìn dáng (YOLO)
        self.shape_predictor = BodyShapePredictor(model_path="best.pt")
        # self.imbalance_detector = ImbalanceDetector() # GIỮ NGUYÊN NẾU CÓ
        
    def generate_report(self, frame, keypoints):
        try:
            # 1. Tính bề ngang vai thực tế bằng Pixel từ khung xương MediaPipe
            shoulder_width_px = 0
            if keypoints and 'left_shoulder' in keypoints and 'right_shoulder' in keypoints:
                ls = keypoints['left_shoulder']
                rs = keypoints['right_shoulder']
                # Định lý Pytago tính khoảng cách 2 điểm
                shoulder_width_px = math.sqrt((ls['x'] - rs['x'])**2 + (ls['y'] - rs['y'])**2)
            
            # 2. Quăng ảnh camera và độ rộng vai cho YOLO phán xử
            shape_report = self.shape_predictor.predict(frame, shoulder_width_px)
            
            # 3. Gom kết quả lỗi vẹo (nếu có)
            # imbalances = self.imbalance_detector.detect_imbalance(keypoints) if keypoints else []

            return {
                "status": "success",
                "body_type": shape_report["body_shape"],
                "general_description": shape_report["description"],
                # "imbalance_issues": imbalances # GIỮ NGUYÊN NẾU CÓ
            }
        except Exception as e:
            print(f"Lỗi BodyAnalyzer: {e}")
            return {"status": "error"}