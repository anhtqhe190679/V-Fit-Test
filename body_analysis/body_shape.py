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
            # 1. Khởi tạo kiến trúc mạng (Mặc định dùng ResNet18)
            self.model = models.resnet18(pretrained=False)
            
            # Thay đổi lớp cuối (Fully Connected) cho 3 classes: V, Nhat, Le
            num_ftrs = self.model.fc.in_features
            self.model.fc = nn.Linear(num_ftrs, 3) 
            
            # 2. Nạp trọng số (state_dict) vào bộ khung một cách an toàn
            state_dict = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            
            # 3. Đưa model vào chế độ dự đoán (eval)
            self.model.to(self.device)
            self.model.eval()
            print("[*] Load model thanh cong!")
            
            # 4. Thiết lập bộ lọc ảnh chuẩn của PyTorch
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
            # Tên nhãn (Sắp xếp theo đúng thứ tự lúc bạn train model)
            self.classes = ["CHU V", "CHU NHAT", "QUA LE"]
            
        except Exception as e:
            print(f"[!] Loi load model: {e}")
            self.model = None

    def predict(self, frame):
        if self.model is None or frame is None:
            return "Chua xac dinh"
            
        try:
            # Chuyển đổi khung hình OpenCV (BGR) sang PIL Image (RGB)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_frame)
            
            # Chuyển thành Tensor và đẩy vào GPU/CPU
            input_tensor = self.transform(pil_img).unsqueeze(0).to(self.device)
            
            # Phân tích
            with torch.no_grad():
                outputs = self.model(input_tensor)
                _, preds = torch.max(outputs, 1)
                return self.classes[preds[0].item()]
        except Exception as e:
            print(f"[!] Loi du doan: {e}")
            return "Chua xac dinh"