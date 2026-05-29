# File: body_analysis/body_shape_predictor.py
import torch
import cv2
from torchvision import transforms
from PIL import Image

class BodyShapePredictor:  # <--- ĐÃ ĐỔI TÊN Ở ĐÂY
    def __init__(self, model_path="bmi_finetuned_model.pth"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[*] Dang load Body Shape Model tren: {self.device}...")
        
        try:
            self.model = torch.load(model_path, map_location=self.device)
            self.model.eval()
            print("[+] Load Model thanh cong!")
        except Exception as e:
            print(f"[!] Loi load model: {e}")
            self.model = None
            
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def predict_body_shape(self, frame):
        if self.model is None or frame is None:
            return "Loi Model hoac Khong co anh"
            
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(rgb_frame)
            input_tensor = self.transform(pil_img).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(input_tensor)
                _, predicted = torch.max(outputs, 1)
                class_id = predicted.item()
                
                shape_labels = {
                    0: "Dang chu V (The thao)", 
                    1: "Dang chu nhat", 
                    2: "Dang qua le"
                }
                return shape_labels.get(class_id, f"Class {class_id}")
                
        except Exception as e:
            print(f"Loi du doan: {e}")
            return "Loi phan tich AI"