import cv2
import time
from datetime import datetime, timezone

from ai.vision.face_detector import FaceMeshDetector
from ai.vision.drowsiness import DrowsinessDetector, calculate_ear
from ai.vision.yawning import YawnDetector, calculate_mar
from ai.vision.head_pose import HeadPoseEstimator
from ai.vision.object_detector import ObjectDetector

from ai.personalization.calibration import CalibrationManager
from ai.personalization.adaptive_thresholds import AdaptiveThresholdEngine
from ai.fusion.weighted_fusion import WeightedFusionEngine
from ai.context.road_risk import RoadContextRiskEngine
from ai.scoring.explainable_scorer import ExplainableRiskScorer

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # index
    (5, 9), (9, 10), (10, 11), (11, 12),   # middle
    (9, 13), (13, 14), (14, 15), (15, 16), # ring
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20) # pinky
]

class ResearchDriverMonitoringEngine:
    """
    Core Research Pipeline: Personalized + Weighted Multimodal Driver Risk Assessment.
    Integrates real-time face mesh, hand tracking, cell phone detection,
    adaptive baseline protection, active weight re-normalization, and explainable risk scoring.
    """
    def __init__(self, calibration_duration_sec=30):
        self.face_detector = FaceMeshDetector()
        self.drowsiness_detector = DrowsinessDetector()
        self.yawn_detector = YawnDetector()
        self.head_pose_estimator = HeadPoseEstimator()
        self.object_detector = ObjectDetector()

        self.calibration_manager = CalibrationManager(duration_sec=calibration_duration_sec)
        self.threshold_engine = AdaptiveThresholdEngine()
        self.fusion_engine = WeightedFusionEngine()
        self.context_engine = RoadContextRiskEngine()
        self.scorer = ExplainableRiskScorer()

    def _draw_hands_and_objects(self, annotated_frame, object_info):
        """Draws hand landmarks, hand bounding boxes, phone bounding boxes, and HUD status."""
        # 1. Draw Hand Tracking
        if object_info.get("detected_hands"):
            for hand in object_info["detected_hands"]:
                lms = hand["landmarks"]
                # Connections
                for p1, p2 in HAND_CONNECTIONS:
                    if p1 < len(lms) and p2 < len(lms):
                        cv2.line(annotated_frame, lms[p1], lms[p2], (0, 255, 128), 2)
                # Landmark joints
                for pt in lms:
                    cv2.circle(annotated_frame, pt, 3, (0, 220, 255), -1)

                # Bounding box
                hx, hy, hw, hh = hand["bbox"]
                h_name = str(hand.get("handedness", "Hand")).upper()
                hlabel = f"HAND ({h_name})"
                cv2.rectangle(annotated_frame, (hx, hy), (hx + hw, hy + hh), (0, 255, 128), 2)
                cv2.putText(annotated_frame, hlabel, (hx, max(20, hy - 6)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 128), 1)

        # 2. Draw Phone Bounding Boxes
        if object_info.get("phone_boxes"):
            for pbox in object_info["phone_boxes"]:
                px, py, pw, ph = pbox["bbox"]
                label = pbox.get("label", "PHONE")
                cv2.rectangle(annotated_frame, (px, py), (px + pw, py + ph), (0, 0, 255), 2)
                cv2.putText(annotated_frame, label, (px, max(20, py - 8)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)

        # 3. HUD - Phone Status
        if object_info.get("possible_phone_detected"):
            p_text = f"PHONE: {object_info.get('phone_reason', 'IN USE')}"
            cv2.putText(annotated_frame, p_text, (20, 125),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
        else:
            cv2.putText(annotated_frame, "PHONE: NOT IN USE", (20, 125),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (16, 185, 129), 1)

        # 4. HUD - Hands Status
        hand_count = object_info.get("hand_count", 0)
        hand_color = (16, 185, 129) if hand_count > 0 else (140, 140, 140)
        hand_text = f"HANDS: {hand_count} DETECTED" if hand_count > 0 else "HANDS: NOT DETECTED"
        cv2.putText(annotated_frame, hand_text, (20, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, hand_color, 1)

        # 5. HUD - Gesture indicator (bare hand near ear without phone)
        if object_info.get("hand_near_ear") and not object_info.get("possible_phone_detected"):
            cv2.putText(annotated_frame, "GESTURE: HAND NEAR EAR (NO PHONE)", (20, 175),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 200, 0), 1)

    def process_frame(self, frame, heart_rate=None, spo2=None, speed=None, acceleration=None, lat=None, lon=None):
        """
        Processes a single camera frame locally through the research pipeline.
        """
        detection = self.face_detector.process(frame)
        annotated_frame = frame.copy()

        if not detection:
            # Face missing state - still run object & hand detection!
            object_info = self.object_detector.update(frame, None)
            self._draw_hands_and_objects(annotated_frame, object_info)

            score_info = {
                "score": 60,
                "level": "MODERATE",
                "color": "#f59e0b",
                "contributors": [{"factor": "Driver Face Missing", "impact": "+60 pts", "detail": "Face not detected in camera view"}],
                "missing_modalities": ["Camera Vision (FACE_MISSING)", "Biometric Sensors (NOT_CONNECTED)", "Vehicle Telemetry (NOT_CONNECTED)", "GPS Context (NOT_CONNECTED)"],
                "modality_weights": {"vision": 1.0, "biometric": 0.0, "vehicle": 0.0, "context": 0.0}
            }
            cv2.putText(annotated_frame, "NO DRIVER FACE DETECTED", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            return {
                "frame": annotated_frame,
                "person_count": 0,
                "face_detected": False,
                "driver_status": "face_missing",
                "calibration": self.calibration_manager.get_status(),
                "metrics": {
                    "ear": 0.0, "left_ear": 0.0, "right_ear": 0.0, "perclos_pct": 0.0, "blink_count": 0,
                    "mar": 0.0, "yaw": 0.0, "pitch": 0.0, "roll": 0.0, "head_orientation": "unknown",
                    "posture_status": "UNKNOWN",
                    "hands_detected": object_info.get("hands_detected", False),
                    "hand_count": object_info.get("hand_count", 0),
                    "hand_near_ear": object_info.get("hand_near_ear", False),
                    "phone_detected": object_info.get("possible_phone_detected", False),
                    "phone_status": object_info.get("phone_status", "PHONE: NOT IN USE"),
                    "phone_reason": object_info.get("phone_reason", ""),
                    "phone_confidence": object_info.get("phone_confidence", 0.0),
                    "drinking_detected": object_info.get("possible_drinking_detected", False),
                    "attention_percentage": 0.0
                },
                "score_info": score_info,
                "event": {
                    "event_type": "face_missing",
                    "severity": "medium",
                    "confidence": 0.99,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }

        # Draw Bounding Box and Extract Sub-landmarks
        annotated_frame = self.face_detector.draw(annotated_frame, detection)
        image_size = detection["image_size"]

        # Use direct landmark keys from face_detector
        left_eye  = detection["left_eye"]
        right_eye = detection["right_eye"]
        mouth     = detection["mouth"]
        landmarks = detection["landmarks"]

        # 1. Compute Raw Vision Metrics
        drowsy_info  = self.drowsiness_detector.update(left_eye, right_eye)
        yawn_info    = self.yawn_detector.update(mouth)
        head_info    = self.head_pose_estimator.update(landmarks, image_size)
        object_info  = self.object_detector.update(frame, detection)

        ear_val = drowsy_info["ear"]
        mar_val = yawn_info["mar"]
        yaw_val = head_info["yaw"]

        # 2. Update / Retrieve Calibration & Profile Status
        calib_status = self.calibration_manager.update(ear_val, mar_val, yaw_val)
        driver_profile = self.calibration_manager.profile

        # 3. Calculate Personalized Deviations
        deviations = self.threshold_engine.evaluate_deviations(ear_val, mar_val, yaw_val, driver_profile)

        # 4. Classify Primary Driver Status
        if drowsy_info["is_drowsy"] or deviations["is_ear_abnormal"]:
            driver_status = "drowsy"
        elif head_info["is_distracted"] or deviations["is_yaw_abnormal"]:
            driver_status = "distracted"
        elif yawn_info["is_yawning"] or deviations["is_mar_abnormal"]:
            driver_status = "yawning"
        elif object_info["possible_phone_detected"]:
            driver_status = "possible_phone_use"
        elif object_info["possible_drinking_detected"]:
            driver_status = "possible_drinking"
        else:
            driver_status = "normal"

        # 5. Process Adaptive Baseline Update (Freezes baseline during abnormal states)
        self.threshold_engine.process_adaptation(ear_val, mar_val, yaw_val, driver_status, driver_profile)

        # 6. Weighted Multimodal Fusion
        fusion_result = self.fusion_engine.fuse(
            deviations["ear_deviation"],
            deviations["mar_deviation"],
            deviations["yaw_deviation"],
            object_info["possible_phone_detected"],
            object_info["possible_drinking_detected"],
            drowsy_info["is_drowsy"],
            vision_confidence=0.95,
            heart_rate=heart_rate,
            spo2=spo2,
            speed=speed,
            acceleration=acceleration
        )

        # 7. Tier 4 Spatial Road Risk Context Adjustment
        context_result = self.context_engine.evaluate_context(
            fusion_result["fused_risk"], lat=lat, lon=lon
        )
        fusion_result["fused_risk"] = context_result["adjusted_risk"]

        # 8. Explainable Driver Risk Score Calculation
        score_info = self.scorer.compute_explainable_score(fusion_result, deviations)

        # Overlay HUD on Frame
        cv2.putText(annotated_frame, f"STATUS: {driver_status.upper()}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (6, 182, 212), 2)
        cv2.putText(annotated_frame, f"EAR: {ear_val:.3f} (μ: {driver_profile.ear_mean:.3f})", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
        cv2.putText(annotated_frame, f"RISK SCORE: {score_info['score']} / 100 ({score_info['level']})", (20, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (16, 185, 129), 2)

        # Draw Hands, Phone, and Gestures
        self._draw_hands_and_objects(annotated_frame, object_info)

        # Calculate forward attention percentage
        attention_pct = 100.0 if head_info["orientation"] == "LOOKING_FORWARD" else 40.0
        hand_count = object_info.get("hand_count", 0)

        return {
            "frame": annotated_frame,
            "person_count": detection.get("person_count", 1),
            "face_detected": True,
            "driver_status": driver_status,
            "calibration": calib_status,
            "profile": driver_profile.to_dict(),
            "metrics": {
                "ear": ear_val,
                "left_ear": drowsy_info.get("left_ear", ear_val),
                "right_ear": drowsy_info.get("right_ear", ear_val),
                "perclos_pct": drowsy_info.get("perclos_pct", 0.0),
                "blink_count": drowsy_info.get("blink_count", 0),
                "mar": mar_val,
                "yaw": yaw_val,
                "pitch": head_info["pitch"],
                "roll": head_info["roll"],
                "head_orientation": head_info.get("orientation", "LOOKING_FORWARD"),
                "posture_status": head_info.get("posture_status", "NORMAL"),
                "hands_detected": object_info.get("hands_detected", False),
                "hand_count": hand_count,
                "hand_near_ear": object_info.get("hand_near_ear", False),
                "phone_status": object_info.get("phone_status", "PHONE: NOT IN USE"),
                "phone_detected": object_info.get("possible_phone_detected", False),
                "phone_reason": object_info.get("phone_reason", ""),
                "calling_detected": "CALL" in object_info.get("phone_reason", ""),
                "drinking_status": object_info.get("drinking_status", "DRINKING: NOT CONFIRMED"),
                "drinking_detected": object_info.get("possible_drinking_detected", False),
                "attention_percentage": attention_pct
            },
            "deviations": deviations,
            "fusion": fusion_result,
            "score_info": score_info,
            "event": {
                "event_type": driver_status,
                "severity": "high" if score_info["score"] >= 65 else ("medium" if score_info["score"] >= 35 else "low"),
                "confidence": 0.95,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
