import torch
import torchvision.models as models
import torch.nn as nn
import cv2
from torchvision import transforms
from PIL import Image

class BodyShapePredictor:
    def __init__(self, model_path="bmi_finetuned_model.pth"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[*] Dang load Body Shape Model tren: {self.device}...")
        try:
            # 1. Dựng lại bộ khung ResNet50
            self.model = models.resnet50(pretrained=False)
            
            # 2. KHÔI PHỤC CHÍNH XÁC PHẦN ĐUÔI (CLASSIFIER) LÚC TRAIN
            num_ftrs = self.model.fc.in_features
            self.model.fc = nn.Sequential(
                nn.Dropout(0.5),          # Đây chính là lớp fc.0 ngầm định
                nn.Linear(num_ftrs, 3)    # Đây chính là lớp fc.1 (chứa weight và bias)
            )
            
            # 3. Nạp trọng số (.pth) và đóng băng mô hình
            state_dict = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            self.model.to(self.device)
            self.model.eval()
            print("[*] Load model thanh cong!")
            
            # 4. Cấu hình tiền xử lý ảnh chuẩn xác
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
            self.classes = ["CHU V", "CHU NHAT", "QUA LE"]
            
        except Exception as e:
            print(f"[!] Loi load model: {e}")
            self.model = None

    def predict(self, frame):
        if self.model is None or frame is None:
            return "Chua xac dinh"
            
        try:
            # 1. CẮT ẢNH VUÔNG Ở GIỮA ĐỂ KHÔNG BỊ MÉO DÁNG
            h, w, _ = frame.shape
            min_dim = min(h, w)
            start_x = (w - min_dim) // 2
            start_y = (h - min_dim) // 2
            cropped_frame = frame[start_y:start_y+min_dim, start_x:start_x+min_dim]
            
            # 2. Xử lý ảnh như bình thường
            rgb_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_frame)
            input_tensor = self.transform(pil_img).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(input_tensor)
                _, preds = torch.max(outputs, 1)
                return self.classes[preds[0].item()]
        except Exception as e:
            print(f"[!] Loi du doan: {e}")
            return "Chua xac dinh"