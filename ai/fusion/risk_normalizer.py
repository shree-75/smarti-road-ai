import numpy as np

class RiskNormalizer:
    """
    Normalizes raw feature deviations and sensor metrics into standardized risk components R_i ∈ [0.0, 1.0].
    """
    @staticmethod
    def normalize_vision_risk(ear_dev, mar_dev, yaw_dev, object_phone, object_drink, is_drowsy_state):
        """
        Computes normalized sub-risk components for computer vision.
        """
        # Drowsiness Risk: Normalized based on EAR drop below baseline
        # Max drop expected: 0.15 below baseline
        r_drowsy = min(1.0, max(0.0, ear_dev / 0.15)) if ear_dev > 0 else 0.0
        if is_drowsy_state:
            r_drowsy = max(r_drowsy, 0.85)

        # Distraction Risk: Normalized based on yaw deviation
        r_distract = min(1.0, max(0.0, yaw_dev / 35.0))

        # Yawning Risk: Normalized based on MAR increase above baseline
        r_yawn = min(1.0, max(0.0, mar_dev / 0.35)) if mar_dev > 0 else 0.0

        # Object Interaction Risks
        r_phone = 0.85 if object_phone else 0.0
        r_drink = 0.70 if object_drink else 0.0

        # Consolidated Vision Category Risk
        r_vision_total = min(1.0, 0.4 * r_drowsy + 0.25 * r_distract + 0.15 * r_yawn + 0.15 * r_phone + 0.05 * r_drink)

        return {
            "r_drowsy": round(r_drowsy, 2),
            "r_distract": round(r_distract, 2),
            "r_yawn": round(r_yawn, 2),
            "r_phone": round(r_phone, 2),
            "r_drink": round(r_drink, 2),
            "r_vision_total": round(r_vision_total, 2)
        }

    @staticmethod
    def normalize_biometric_risk(heart_rate=None, spo2=None):
        """
        Computes normalized biometric category risk if physical sensors are connected.
        Returns None if hardware is unavailable.
        """
        if heart_rate is None and spo2 is None:
            return None

        r_hr = 0.0
        if heart_rate is not None:
            # HR < 55 (bradycardia / drowsiness) or > 110 (stress / panic)
            if heart_rate < 55:
                r_hr = min(1.0, (55 - heart_rate) / 20.0)
            elif heart_rate > 100:
                r_hr = min(1.0, (heart_rate - 100) / 40.0)

        r_spo2 = 0.0
        if spo2 is not None and spo2 < 95:
            r_spo2 = min(1.0, (95 - spo2) / 10.0)

        r_biometric_total = max(r_hr, r_spo2)
        return {
            "r_hr": round(r_hr, 2),
            "r_spo2": round(r_spo2, 2),
            "r_biometric_total": round(r_biometric_total, 2)
        }

    @staticmethod
    def normalize_vehicle_risk(speed=None, acceleration=None):
        """
        Computes normalized vehicle telemetry risk if vehicle sensors are connected.
        Returns None if hardware is unavailable.
        """
        if speed is None and acceleration is None:
            return None

        r_speed = 0.0
        if speed is not None and speed > 80:
            r_speed = min(1.0, (speed - 80) / 40.0)

        r_accel = 0.0
        if acceleration is not None and acceleration > 2.0:
            r_accel = min(1.0, (acceleration - 2.0) / 3.0)

        r_vehicle_total = max(r_speed, r_accel)
        return {
            "r_speed": round(r_speed, 2),
            "r_accel": round(r_accel, 2),
            "r_vehicle_total": round(r_vehicle_total, 2)
        }
