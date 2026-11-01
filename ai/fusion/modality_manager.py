from ai.config import VISION_WEIGHT, BIOMETRIC_WEIGHT, VEHICLE_WEIGHT, ROAD_CONTEXT_WEIGHT

class ModalityManager:
    """
    Manages active vs missing sensor modalities, computes modality reliability scores,
    and performs dynamic weight re-normalization:
      EffectiveWeight_i = BaseWeight_i * Reliability_i
      NormalizedWeight_i = EffectiveWeight_i / ∑ EffectiveWeight_j
    """
    def __init__(self):
        self.raw_weights = {
            "vision": VISION_WEIGHT,
            "biometric": BIOMETRIC_WEIGHT,
            "vehicle": VEHICLE_WEIGHT,
            "context": ROAD_CONTEXT_WEIGHT
        }

    def evaluate_modalities(self, camera_active=True, biometric_active=False, vehicle_active=False, context_active=False):
        """
        Calculates status, reliability scores, and dynamically re-normalized weights.
        """
        status = {
            "vision": "ACTIVE" if camera_active else "DISCONNECTED",
            "biometric": "ACTIVE" if biometric_active else "N/A — HARDWARE OFFLINE",
            "vehicle": "ACTIVE" if vehicle_active else "N/A — HARDWARE OFFLINE",
            "context": "ACTIVE" if context_active else "N/A — HARDWARE OFFLINE"
        }

        reliability = {
            "vision": 0.95 if camera_active else 0.0,
            "biometric": 0.90 if biometric_active else 0.0,
            "vehicle": 0.90 if vehicle_active else 0.0,
            "context": 0.85 if context_active else 0.0
        }

        # Calculate effective un-normalized weight = BaseWeight * Reliability
        effective_raw = {
            mod: self.raw_weights[mod] * reliability[mod]
            for mod in status.keys()
        }

        effective_sum = sum(effective_raw.values())

        # Normalize weights so they sum to 1.0 across active modalities
        effective_weights = {}
        for mod in status.keys():
            if effective_sum > 0:
                effective_weights[mod] = round(effective_raw[mod] / effective_sum, 3)
            else:
                effective_weights[mod] = 0.0

        return {
            "modality_status": status,
            "reliability_scores": reliability,
            "raw_weights": self.raw_weights,
            "effective_weights": effective_weights,
            "active_count": sum(1 for stat in status.values() if stat == "ACTIVE")
        }
