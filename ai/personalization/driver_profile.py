import numpy as np

class DriverProfile:
    """
    Encapsulates a driver's personalized anatomical & behavioral baseline statistics.
    """
    def __init__(self, driver_id="default_driver"):
        self.driver_id = driver_id
        self.is_calibrated = False
        
        # Baseline statistical parameters
        self.ear_mean = 0.30
        self.ear_std = 0.03
        self.mar_mean = 0.18
        self.mar_std = 0.04
        self.yaw_mean = 0.0
        self.yaw_std = 5.0
        
        self.calibration_samples_count = 0

    def update_from_samples(self, ear_samples, mar_samples, yaw_samples):
        """
        Calculates driver baseline parameters from calibration sample arrays.
        """
        if len(ear_samples) > 0:
            self.ear_mean = float(np.mean(ear_samples))
            self.ear_std = max(0.01, float(np.std(ear_samples)))

        if len(mar_samples) > 0:
            self.mar_mean = float(np.mean(mar_samples))
            self.mar_std = max(0.01, float(np.std(mar_samples)))

        if len(yaw_samples) > 0:
            self.yaw_mean = float(np.mean(yaw_samples))
            self.yaw_std = max(1.0, float(np.std(yaw_samples)))

        self.calibration_samples_count = len(ear_samples)
        self.is_calibrated = True

    def adapt_baseline(self, current_ear, current_mar, current_yaw, rate=0.02):
        """
        Slowly updates baseline parameters during STABLE/NORMAL driving conditions only.
        """
        if not self.is_calibrated:
            return

        self.ear_mean = (1 - rate) * self.ear_mean + rate * current_ear
        self.mar_mean = (1 - rate) * self.mar_mean + rate * current_mar
        self.yaw_mean = (1 - rate) * self.yaw_mean + rate * current_yaw

    def to_dict(self):
        return {
            "driver_id": self.driver_id,
            "is_calibrated": self.is_calibrated,
            "ear_baseline": {"mean": round(self.ear_mean, 3), "std": round(self.ear_std, 3)},
            "mar_baseline": {"mean": round(self.mar_mean, 3), "std": round(self.mar_std, 3)},
            "yaw_baseline": {"mean": round(self.yaw_mean, 1), "std": round(self.yaw_std, 1)},
            "samples_collected": self.calibration_samples_count
        }
