from ai.config import EAR_SIGMA_FACTOR, MAR_SIGMA_FACTOR, YAW_DEVIATION_FACTOR, ADAPTATION_RATE

class AdaptiveThresholdEngine:
    """
    Evaluates current driver measurements against the driver's personalized baseline statistics.
    Computes standardized Z-score deviations and controls baseline adaptation protection.
    """
    def __init__(self, ear_k=EAR_SIGMA_FACTOR, mar_k=MAR_SIGMA_FACTOR, yaw_k=YAW_DEVIATION_FACTOR):
        self.ear_k = ear_k
        self.mar_k = mar_k
        self.yaw_k = yaw_k

    def compute_personalized_thresholds(self, profile):
        """
        Computes dynamic personalized threshold bounds for the driver.
        """
        ear_thresh = max(0.12, profile.ear_mean - (self.ear_k * profile.ear_std))
        mar_thresh = min(0.80, profile.mar_mean + (self.mar_k * profile.mar_std))
        yaw_max = profile.yaw_std * self.yaw_k + 15.0

        return {
            "ear_threshold": round(ear_thresh, 3),
            "mar_threshold": round(mar_thresh, 3),
            "yaw_threshold": round(yaw_max, 1)
        }

    def evaluate_deviations(self, current_ear, current_mar, current_yaw, profile):
        """
        Calculates raw and standardized Z-score feature deviations relative to driver's baseline statistics.
        Formula:
          Z_EAR = (μ_EAR - EAR_current) / σ_EAR
          Z_MAR = (MAR_current - μ_MAR) / σ_MAR
          Z_Yaw = |Yaw_current - μ_Yaw| / σ_Yaw
        """
        thresholds = self.compute_personalized_thresholds(profile)

        ear_dev = profile.ear_mean - current_ear
        mar_dev = current_mar - profile.mar_mean
        yaw_dev = abs(current_yaw - profile.yaw_mean)

        # Standardized Z-score deviations
        z_ear = ear_dev / max(0.005, profile.ear_std)
        z_mar = mar_dev / max(0.005, profile.mar_std)
        z_yaw = yaw_dev / max(0.5, profile.yaw_std)

        is_ear_abnormal = current_ear < thresholds["ear_threshold"]
        is_mar_abnormal = current_mar > thresholds["mar_threshold"]
        is_yaw_abnormal = yaw_dev > thresholds["yaw_threshold"]

        return {
            "ear_deviation": round(ear_dev, 3),
            "mar_deviation": round(mar_dev, 3),
            "yaw_deviation": round(yaw_dev, 1),
            "z_score_ear": round(z_ear, 2),
            "z_score_mar": round(z_mar, 2),
            "z_score_yaw": round(z_yaw, 2),
            "thresholds": thresholds,
            "is_ear_abnormal": is_ear_abnormal,
            "is_mar_abnormal": is_mar_abnormal,
            "is_yaw_abnormal": is_yaw_abnormal
        }

    def process_adaptation(self, current_ear, current_mar, current_yaw, driver_state, profile):
        """
        Adapts driver baseline ONLY during NORMAL state.
        Freezes baseline updates during DROWSY, DISTRACTED, or abnormal risk states.
        """
        if driver_state == "normal" and profile.is_calibrated:
            profile.adapt_baseline(current_ear, current_mar, current_yaw, rate=ADAPTATION_RATE)
            return {"baseline_adapted": True, "reason": "Normal state - slow adaptation applied"}
        else:
            return {"baseline_adapted": False, "reason": f"Baseline frozen during {driver_state.upper()} state"}
