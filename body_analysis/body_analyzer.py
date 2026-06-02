import math
from ultralytics import YOLO
from config import ModelConfig
from body_analysis.imbalance_detector import ImbalanceDetector 

class BodyAnalyzer:
    def __init__(self):
        # Chỉ load 1 mô hình Pose duy nhất cho toàn bộ App (Siêu nhẹ)
        model_path = ModelConfig.MODEL_PATHS["pose"]
        self.model = YOLO(model_path)
        self.imbalance_detector = ImbalanceDetector(tilt_threshold=20.0)

    def calculate_distance(self, p1, p2):
        """Hàm tính khoảng cách giữa 2 điểm (Pixel)"""
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

    def generate_report(self, frame, height_cm=170, weight_kg=60):
        """
        Phân tích dáng người dựa vào AI Pose + Chỉ số cơ thể thực tế
        """
        # Chạy YOLO Pose
        results = self.model(frame, verbose=False)[0]
        
        report = {
            "status": "failed",
            "body_shape": "Chua xac dinh",
            "general_description": "YOLO không tìm thấy cơ thể bạn. Hãy lùi ra xa nhé!"
        }

        if len(results.boxes) == 0 or results.keypoints is None:
            return report

        # Lấy tọa độ các khớp (Index theo chuẩn YOLO: 5=Vai trái, 6=Vai phải, 11=Hông trái, 12=Hông phải)
        # Lưu ý: YOLO trả về danh sách các người, lấy người đầu tiên [0]
        keypoints = results.keypoints.xy[0].cpu().numpy()
        
        try:
            # 1. AI TÍNH TỶ LỆ CƠ THỂ
            l_shoulder, r_shoulder = keypoints[5], keypoints[6]
            l_hip, r_hip = keypoints[11], keypoints[12]
            
            shoulder_width = self.calculate_distance(l_shoulder, r_shoulder)
            hip_width = self.calculate_distance(l_hip, r_hip)
            
            # Tỷ lệ Vai / Hông
            ratio = shoulder_width / hip_width if hip_width > 0 else 1.0

            # 2. TOÁN HỌC TÍNH BMI
            bmi = weight_kg / ((height_cm / 100) ** 2)

            # 3. KẾT HỢP ĐỂ ĐƯA RA KẾT LUẬN
            report["status"] = "success"
            
            if bmi < 18.5:
                report["body_shape"] = "DANG NGUOI GAY (Thieu can)"
                report["general_description"] = f"BMI: {bmi:.1f} - Thieu co bap, can tap trung an uong va cac bai tap tang co (Hypertrophy)."
            elif bmi >= 25.0:
                if ratio < 0.95:
                    report["body_shape"] = "DANG QUA LE (Thua can)"
                    report["general_description"] = f"BMI: {bmi:.1f} - Mo tap trung o mong/dui. Can tap trung cardio dot calo toan than."
                else:
                    report["body_shape"] = "DANG CHU O / BEO TONG THE"
                    report["general_description"] = f"BMI: {bmi:.1f} - Can dieu chinh che do an tham hut calo (Caloric Deficit)."
            else:
                # BMI Bình thường (18.5 -> 24.9)
                if ratio > 1.15:
                    report["body_shape"] = "DANG CHU V (The thao)"
                    report["general_description"] = f"BMI: {bmi:.1f} - Ti le co the dep, vai rong hon hong. Tiep tuc duy tri tap luyen."
                else:
                    report["body_shape"] = "DANG CHU NHAT (Can doi)"
                    report["general_description"] = f"BMI: {bmi:.1f} - Can nang on dinh nhung thieu duong cong. Nen tap them vai va mong."

            print(f"[AI INFO] BMI: {bmi:.1f} | Ty le Vai/Hong: {ratio:.2f}")

        except Exception as e:
            report["general_description"] = "Khong thay ro cac khop Vai va Hong."
            
        return report