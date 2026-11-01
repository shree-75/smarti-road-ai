from ai.config import HOTSPOT_RISK_MULTIPLIER

class RoadContextRiskEngine:
    """
    Tier 4 Spatial & Environmental Context Risk Engine Interface.
    Applies situational context multipliers (accident hotspots, night driving, weather) to multimodal risk scores.
    """
    def __init__(self):
        self.is_connected = False

    def evaluate_context(self, fused_risk, lat=None, lon=None, time_of_day=None, weather=None):
        """
        Applies road context multipliers to the multimodal risk score.
        Returns unmodified fused_risk if GPS / GIS context inputs are unavailable.
        """
        if lat is None or lon is None:
            return {
                "context_connected": False,
                "context_multiplier": 1.0,
                "adjusted_risk": fused_risk,
                "reasons": ["GPS / Spatial Context NOT CONNECTED"]
            }

        multiplier = 1.0
        reasons = []

        # Placeholder logic for Tier 4 spatial hotspot matching
        # When connected to real GIS database, check distance to accident cluster coordinates
        is_hotspot = False
        if is_hotspot:
            multiplier *= HOTSPOT_RISK_MULTIPLIER
            reasons.append(f"Vehicle in Accident Hotspot Zone (*{HOTSPOT_RISK_MULTIPLIER}x)")

        adjusted_risk = min(1.0, fused_risk * multiplier)
        return {
            "context_connected": True,
            "context_multiplier": round(multiplier, 2),
            "adjusted_risk": round(adjusted_risk, 3),
            "reasons": reasons
        }
