import time
from ai.config import CALIBRATION_DURATION_SEC
from ai.personalization.driver_profile import DriverProfile

class CalibrationManager:
    """
    Manages the initial 30–60 second driver baseline calibration phase.
    """
    def __init__(self, duration_sec=CALIBRATION_DURATION_SEC):
        self.duration_sec = duration_sec
        self.start_time = None
        self.is_active = False
        self.profile = DriverProfile()
        
        self.ear_samples = []
        self.mar_samples = []
        self.yaw_samples = []

    def start_calibration(self):
        self.start_time = time.time()
        self.is_active = True
        self.ear_samples.clear()
        self.mar_samples.clear()
        self.yaw_samples.clear()

    def update(self, ear, mar, yaw):
        if not self.is_active:
            if self.start_time is None:
                self.start_calibration()
            else:
                return self.get_status()

        elapsed = time.time() - self.start_time
        if elapsed < self.duration_sec:
            # Collect valid non-zero calibration samples
            if ear > 0.05:
                self.ear_samples.append(ear)
            if mar > 0.01:
                self.mar_samples.append(mar)
            self.yaw_samples.append(yaw)
        else:
            # Complete Calibration Phase
            self.profile.update_from_samples(self.ear_samples, self.mar_samples, self.yaw_samples)
            self.is_active = False

        return self.get_status()

    def get_status(self):
        if self.start_time is None:
            return {"status": "UNINITIALIZED", "progress_pct": 0, "elapsed_sec": 0}

        elapsed = time.time() - self.start_time
        if self.is_active:
            progress = min(100, int((elapsed / self.duration_sec) * 100))
            return {
                "status": "CALIBRATING",
                "progress_pct": progress,
                "elapsed_sec": round(elapsed, 1),
                "remaining_sec": round(max(0, self.duration_sec - elapsed), 1)
            }
        else:
            return {
                "status": "PERSONALIZED_PROFILE_ACTIVE",
                "progress_pct": 100,
                "elapsed_sec": round(self.duration_sec, 1),
                "profile": self.profile.to_dict()
            }
