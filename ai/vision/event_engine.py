import cv2
import time
from datetime import datetime, timezone
from ai.vision.face_detector import FaceMeshDetector
from ai.vision.drowsiness import DrowsinessDetector
from ai.vision.yawning import YawnDetector
from ai.vision.head_pose import HeadPoseEstimator
from ai.vision.object_detector import ObjectDetector
from ai.vision.safety_score import SafetyScoreEngine

class DriverMonitoringEngine:
    """
    Centralized Edge AI Driver Safety Processing Engine.
    Processes camera frames locally and generates derived driver safety telemetry events.
    """
    def __init__(self):
        self.face_detector = FaceMeshDetector()
        self.drowsiness_detector = DrowsinessDetector()
        self.yawn_detector = YawnDetector()
        self.head_pose_estimator = HeadPoseEstimator()
        self.object_detector = ObjectDetector()
        self.score_engine = SafetyScoreEngine()

    def process_frame(self, frame):
        """
        Analyzes a single camera frame locally on edge device.
        Returns visual annotated frame, telemetry metrics, and active driver safety event objects.
        """
        detection = self.face_detector.process(frame)
        annotated_frame = frame.copy()

        if not detection:
            # Face missing state
            score_data = self.score_engine.compute_score({"face_missing": True})
            cv2.putText(annotated_frame, "NO DRIVER FACE DETECTED", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            return {
                "frame": annotated_frame,
                "face_detected": False,
                "driver_status": "face_missing",
                "ear": 0.0,
                "mar": 0.0,
                "head_orientation": "unknown",
                "safety_score": score_data["score"],
                "score_category": score_data["category"],
                "event": {
                    "event_type": "face_missing",
                    "severity": "medium",
                    "confidence": 0.99,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }

        # Draw Face Bounding Box
        annotated_frame = self.face_detector.draw(annotated_frame, detection)
        image_size = detection["image_size"]

        # Extract Landmark subsets directly from detection
        left_eye = detection["left_eye"]
        right_eye = detection["right_eye"]
        mouth = detection["mouth"]

        # 1. Drowsiness & EAR
        drowsy_info = self.drowsiness_detector.update(left_eye, right_eye)

        # 2. Yawning & MAR
        yawn_info = self.yawn_detector.update(mouth)

        # 3. Head Pose & Distraction
        head_info = self.head_pose_estimator.update(landmarks, image_size)

        # 4. Object Interaction
        object_info = self.object_detector.update(frame, detection)

        # 5. Compute Safety Score
        behavioral_state = {
            "face_missing": False,
            "is_drowsy": drowsy_info["is_drowsy"],
            "is_distracted": head_info["is_distracted"],
            "is_yawning": yawn_info["is_yawning"],
            "possible_phone_use": object_info["possible_phone_detected"],
            "possible_drinking": object_info["possible_drinking_detected"]
        }

        score_data = self.score_engine.compute_score(behavioral_state)

        # Determine Primary Driver Status & Event Type
        if drowsy_info["is_drowsy"]:
            driver_status = "drowsy"
            event_type = "drowsiness"
            severity = "high"
        elif head_info["is_distracted"]:
            driver_status = "distracted"
            event_type = "driver_distraction"
            severity = "medium"
        elif yawn_info["is_yawning"]:
            driver_status = "yawning"
            event_type = "yawning"
            severity = "low"
        elif object_info["possible_phone_detected"]:
            driver_status = "possible_phone_use"
            event_type = "possible_phone_use"
            severity = "high"
        elif object_info["possible_drinking_detected"]:
            driver_status = "possible_drinking"
            event_type = "possible_drinking"
            severity = "medium"
        else:
            driver_status = "normal"
            event_type = "normal"
            severity = "none"

        # Overlay Info on Annotated Frame
        cv2.putText(annotated_frame, f"Driver Status: {driver_status.upper()}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (6, 182, 212), 2)
        cv2.putText(annotated_frame, f"EAR: {drowsy_info['ear']} | MAR: {yawn_info['mar']}", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
        cv2.putText(annotated_frame, f"Head Pose: {head_info['orientation'].upper()}", (20, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
        cv2.putText(annotated_frame, f"Safety Score: {score_data['score']} ({score_data['category']})", (20, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (16, 185, 129), 2)

        return {
            "frame": annotated_frame,
            "face_detected": True,
            "driver_status": driver_status,
            "ear": drowsy_info["ear"],
            "mar": yawn_info["mar"],
            "head_orientation": head_info["orientation"],
            "safety_score": score_data["score"],
            "score_category": score_data["category"],
            "event": {
                "event_type": event_type,
                "severity": severity,
                "confidence": 0.92,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
