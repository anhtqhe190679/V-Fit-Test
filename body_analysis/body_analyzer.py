# File: body_analysis/body_analyzer.py
from .imbalance_detector import ImbalanceDetector
from .posture_analyzer import PostureAnalyzer

# [ĐÃ SỬA] Import class từ file body_shape.py của bạn
from .body_shape import BodyShapePredictor  

class BodyAnalyzer:
    def __init__(self):
        self.imbalance_detector = ImbalanceDetector(tilt_threshold=20.0)
        self.posture_analyzer = PostureAnalyzer()
        
        # Khởi tạo AI Predictor
        self.shape_predictor = BodyShapePredictor(model_path="bmi_finetuned_model.pth")

    def generate_report(self, frame, keypoints, segmentation_mask=None):
        imbalance_issues = self.imbalance_detector.detect_imbalance(keypoints)
        
        # Đưa ảnh thật (frame) vào model
        body_shape_result = self.shape_predictor.predict_body_shape(frame)
        
        return {
            "imbalances": imbalance_issues,
            "body_shape": body_shape_result # Trả về với key là 'body_shape'
        }