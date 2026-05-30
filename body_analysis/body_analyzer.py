from .posture_analyzer import PostureAnalyzer
from .imbalance_detector import ImbalanceDetector
from .body_shape import BodyShapePredictor  # Import model Deep Learning

class BodyAnalyzer:
    def __init__(self):
        self.posture_analyzer = PostureAnalyzer()
        self.imbalance_detector = ImbalanceDetector(tilt_threshold=20.0)
        self.shape_predictor = BodyShapePredictor() # Khởi tạo model

    # Đã bổ sung đầy đủ tham số đón đầu từ main.py
    def generate_report(self, frame=None, landmarks=None, segmentation_mask=None):
        if not landmarks:
            return {"status": "error", "message": "No landmarks detected."}
            
        try:
            # 1. Phân tích độ Gầy/Béo bằng Posture Analyzer (Toán học & Mask)
            posture_report = self.posture_analyzer.analyze_shape(landmarks, segmentation_mask)
            
            # 2. Nhận diện Dáng (V, Chữ Nhật, Quả Lê) bằng Deep Learning
            dl_body_shape = "Chua xac dinh"
            if frame is not None and self.shape_predictor.model is not None:
                dl_body_shape = self.shape_predictor.predict(frame)
            else:
                dl_body_shape = posture_report.get("body_type", "Chua xac dinh")

            # 3. Phát hiện lệch vẹo xương khớp
            imbalance_issues = self.imbalance_detector.detect_imbalance(landmarks)
            
            # 4. Trả kết quả về cho main.py
            return {
                "status": "success",
                "body_shape": dl_body_shape, # Đồng bộ key body_shape
                "general_description": posture_report.get("description", ""),
                "imbalance_issues": imbalance_issues
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}