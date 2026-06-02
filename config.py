class ModelConfig:
    # 🔴 ĐỔI CHẾ ĐỘ Ở ĐÂY: "pose" (Đo lệch vẹo) hoặc "seg" (Đo dáng người béo/gầy)
    ACTIVE_TASK = "seg"  

    # Khai báo đường dẫn
    MODEL_PATHS = {
        # Pose dùng hàng có sẵn của Ultralytics, tự động tải xuống
        "pose": "yolov8n-pose.pt", 
        
        # Seg dùng "bộ não" bạn vừa thức đêm train xong!
        "seg": "models/seg_best.pt" 
    }

    @classmethod
    def get_model_path(cls):
        return cls.MODEL_PATHS[cls.ACTIVE_TASK]