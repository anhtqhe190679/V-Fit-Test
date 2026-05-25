import cv2
import mediapipe as mp


class PoseEstimator:
    def __init__(
        self,
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        enable_segmentation=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            smooth_landmarks=smooth_landmarks,
            enable_segmentation=enable_segmentation,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def detect(self, frame):
        """
        Input:
            frame: OpenCV BGR image

        Output:
            results from MediaPipe Pose
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False

        results = self.pose.process(rgb_frame)

        rgb_frame.flags.writeable = True
        return results

    def close(self):
        self.pose.close()
