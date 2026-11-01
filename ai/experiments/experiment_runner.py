import time
from ai.experiments.metrics_collector import MetricsCollector

class ExperimentRunner:
    """
    Research Experiment Benchmark Executor.
    Evaluates frame inputs side-by-side across the four research tiers:
      Tier 1: Fixed Threshold + Camera Only
      Tier 2: Personalized Threshold + Camera Only
      Tier 3: Personalized + Weighted Multimodal Fusion
      Tier 4: Personalized + Weighted Multimodal + Spatial Road Risk Context
    """
    def __init__(self):
        self.collector = MetricsCollector()
        self.active_tier = "Tier_3_Weighted_Multimodal" # Default active research tier

    def set_tier(self, tier_name):
        valid_tiers = [
            "Tier_1_Fixed_Vision",
            "Tier_2_Personalized_Vision",
            "Tier_3_Weighted_Multimodal",
            "Tier_4_Multimodal_Road_Context"
        ]
        if tier_name in valid_tiers:
            self.active_tier = tier_name
            return True
        return False

    def evaluate_tier_1_fixed(self, ear, mar, yaw, object_phone, object_drink):
        """
        Tier 1 Execution: Fixed universal thresholds (EAR < 0.21, MAR > 0.55, Yaw > 18°) without baseline calibration.
        """
        is_drowsy = ear < 0.21
        is_yawning = mar > 0.55
        is_distracted = abs(yaw) > 18.0

        score = 0
        contributors = []
        if is_drowsy:
            score += 45
            contributors.append({"factor": "Fixed EAR Threshold (< 0.21)", "impact": "+45 pts"})
        if is_distracted:
            score += 30
            contributors.append({"factor": "Fixed Head Yaw Threshold (> 18°)", "impact": "+30 pts"})
        if is_yawning:
            score += 15
            contributors.append({"factor": "Fixed MAR Threshold (> 0.55)", "impact": "+15 pts"})
        if object_phone:
            score += 25
            contributors.append({"factor": "Phone Proximity", "impact": "+25 pts"})

        score = min(100, score)
        level = "CRITICAL" if score >= 85 else ("HIGH" if score >= 65 else ("MODERATE" if score >= 35 else "LOW"))

        return {
            "tier_mode": "Tier_1_Fixed_Vision",
            "driver_status": "drowsy" if is_drowsy else ("distracted" if is_distracted else "normal"),
            "score_info": {
                "score": score,
                "level": level,
                "color": "#ef4444" if score >= 65 else "#10b981",
                "contributors": contributors,
                "missing_modalities": ["Personalization (DISABLED)", "Biometric Sensors (DISABLED)", "Vehicle Telemetry (DISABLED)", "GPS Context (DISABLED)"],
                "modality_weights": {"vision": 1.0, "biometric": 0.0, "vehicle": 0.0, "context": 0.0}
            }
        }

    def evaluate_current_tier(self, engine, frame, heart_rate=None, spo2=None, speed=None, acceleration=None, lat=None, lon=None):
        """
        Executes frame evaluation according to the selected active research tier.
        """
        start_t = time.time()

        if self.active_tier == "Tier_1_Fixed_Vision":
            # Extract raw metrics and evaluate via fixed threshold
            detection = engine.face_detector.process(frame)
            if not detection:
                result = engine.process_frame(frame)
                result["score_info"]["tier_mode"] = self.active_tier
                return result

            landmarks = detection["landmarks"]
            left_eye = landmarks[engine.face_detector.LEFT_EYE]
            right_eye = landmarks[engine.face_detector.RIGHT_EYE]
            mouth = landmarks[engine.face_detector.MOUTH_INNER]

            ear = engine.drowsiness_detector.update(left_eye, right_eye)["ear"]
            mar = engine.yawn_detector.update(mouth)["mar"]
            head_info = engine.head_pose_estimator.update(landmarks, detection["image_size"])
            object_info = engine.object_detector.update(frame, detection)

            tier1_res = self.evaluate_tier_1_fixed(
                ear, mar, head_info["yaw"],
                object_info["possible_phone_detected"],
                object_info["possible_drinking_detected"]
            )
            
            result = engine.process_frame(frame)
            result["driver_status"] = tier1_res["driver_status"]
            result["score_info"] = tier1_res["score_info"]
            
            latency = (time.time() - start_t) * 1000
            self.collector.log_event(self.active_tier, result["driver_status"], result["score_info"], result["deviations"], result["fusion"]["modality_info"], latency)
            return result

        else:
            # Tiers 2, 3, and 4 execute through ResearchDriverMonitoringEngine
            result = engine.process_frame(
                frame, heart_rate=heart_rate, spo2=spo2, speed=speed, acceleration=acceleration, lat=lat, lon=lon
            )
            result["score_info"]["tier_mode"] = self.active_tier
            
            latency = (time.time() - start_t) * 1000
            deviations = result.get("deviations", {})
            modality_info = result.get("fusion", {}).get("modality_info", {"effective_weights": {"vision": 1.0, "biometric": 0.0, "vehicle": 0.0, "context": 0.0}})
            self.collector.log_event(self.active_tier, result["driver_status"], result["score_info"], deviations, modality_info, latency)
            return result
