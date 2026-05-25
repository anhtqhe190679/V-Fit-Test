from .posture_analyzer import PostureAnalyzer
from .imbalance_detector import ImbalanceDetector

class BodyAnalyzer:
    def __init__(self):
        self.posture_analyzer = PostureAnalyzer()
        self.imbalance_detector = ImbalanceDetector(tilt_threshold=45.0)

    def generate_report(self, landmarks, segmentation_mask=None):
        if not landmarks:
            return {"status": "error", "message": "No landmarks detected."}

        try:
            # 1. Phân tích Dáng người & Ty lệ Mỡ/Cơ (Truyền mask thực tế)
            shape_report = self.posture_analyzer.analyze_shape(landmarks, segmentation_mask)
            
            # 2. Phân tích Độ lệch vẹo xương khớp
            imbalance_issues = self.imbalance_detector.detect_imbalance(landmarks)
            
            # 3. Gom kết quả xuất ra main
            return {
                "status": "success",
                "body_type": shape_report["body_type"],
                "general_description": shape_report["description"],
                "imbalance_issues": imbalance_issues
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}