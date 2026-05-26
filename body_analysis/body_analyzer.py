from .posture_analyzer import PostureAnalyzer
from .imbalance_detector import ImbalanceDetector

class BodyAnalyzer:
    def __init__(self):
        self.posture_analyzer = PostureAnalyzer()
        # FIX QUAN TRỌNG: Chuyển ngưỡng (threshold) từ 45.0 xuống 5.0 để nhạy bén hơn
        self.imbalance_detector = ImbalanceDetector(tilt_threshold=5.0)

    def generate_report(self, landmarks, segmentation_mask=None):
        if not landmarks:
            return {"status": "error", "message": "No landmarks detected."}

        try:
            # 1. Phân tích Dáng người & Ty lệ Mỡ/Cơ
            shape_report = self.posture_analyzer.analyze_shape(landmarks, segmentation_mask)
            
            # 2. Phân tích Độ lệch vẹo xương khớp (Đầu, Vai, Hông, Trục người)
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