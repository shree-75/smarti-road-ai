from ai.fusion.modality_manager import ModalityManager
from ai.fusion.risk_normalizer import RiskNormalizer

class WeightedFusionEngine:
    """
    Weighted Multimodal Sensor Fusion Engine.
    Fuses normalized category risk components using dynamically re-normalized active modality weights.
    Separates Model Confidence (algorithm extraction certainty) from Driver Peril Risk.
    """
    def __init__(self):
        self.modality_manager = ModalityManager()
        self.risk_normalizer = RiskNormalizer()

    def fuse(
        self,
        ear_dev, mar_dev, yaw_dev,
        object_phone, object_drink,
        is_drowsy_state,
        vision_confidence=0.95,
        heart_rate=None, spo2=None,
        speed=None, acceleration=None
    ):
        # 1. Evaluate modality connectivity and calculate effective weights
        biometric_active = heart_rate is not None or spo2 is not None
        vehicle_active = speed is not None or acceleration is not None
        
        modality_info = self.modality_manager.evaluate_modalities(
            camera_active=True,
            biometric_active=biometric_active,
            vehicle_active=vehicle_active,
            context_active=False
        )
        weights = modality_info["effective_weights"]

        # 2. Normalize category risk scores R_i ∈ [0.0, 1.0]
        vision_risk = self.risk_normalizer.normalize_vision_risk(
            ear_dev, mar_dev, yaw_dev, object_phone, object_drink, is_drowsy_state
        )
        biometric_risk = self.risk_normalizer.normalize_biometric_risk(heart_rate, spo2)
        vehicle_risk = self.risk_normalizer.normalize_vehicle_risk(speed, acceleration)

        # 3. Compute Weighted Multimodal Risk Sum R_multimodal
        r_fusion = weights["vision"] * vision_risk["r_vision_total"]
        
        if biometric_risk is not None:
            r_fusion += weights["biometric"] * biometric_risk["r_biometric_total"]
            
        if vehicle_risk is not None:
            r_fusion += weights["vehicle"] * vehicle_risk["r_vehicle_total"]

        final_fused_risk = min(1.0, max(0.0, r_fusion))

        return {
            "fused_risk": round(final_fused_risk, 3),
            "vision_risk": vision_risk,
            "biometric_risk": biometric_risk,
            "vehicle_risk": vehicle_risk,
            "modality_info": modality_info,
            "model_confidence": round(vision_confidence, 2) # Explicit separation of Model Confidence vs Driver Risk
        }
