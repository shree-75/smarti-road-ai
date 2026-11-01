class ExplainableRiskScorer:
    """
    Converts fused risk scores into an explainable 0–100 Driver Risk Score with detailed contributor breakdowns.
    """
    def compute_explainable_score(self, fusion_result, deviations):
        fused_risk = fusion_result["fused_risk"]
        score = int(round(fused_risk * 100))
        score = max(0, min(100, score))

        # Risk Level Classification
        if score >= 85:
            level = "CRITICAL"
            color = "#ef4444"
        elif score >= 65:
            level = "HIGH"
            color = "#f59e0b"
        elif score >= 35:
            level = "MODERATE"
            color = "#06b6d4"
        else:
            level = "LOW"
            color = "#10b981"

        # Explicit Contributor Breakdown
        contributors = []
        vision_risk = fusion_result["vision_risk"]

        if vision_risk["r_drowsy"] > 0.2:
            pts = int(vision_risk["r_drowsy"] * 40)
            contributors.append({
                "factor": "Personalized Eye Closure Deviation",
                "impact": f"+{pts} pts",
                "detail": f"EAR drop Δ: -{deviations['ear_deviation']:.3f} below driver baseline"
            })

        if vision_risk["r_distract"] > 0.2:
            pts = int(vision_risk["r_distract"] * 25)
            contributors.append({
                "factor": "Head Yaw Deviation",
                "impact": f"+{pts} pts",
                "detail": f"Head turned Δ: {deviations['yaw_deviation']:.1f}° away from normal"
            })

        if vision_risk["r_yawn"] > 0.2:
            pts = int(vision_risk["r_yawn"] * 15)
            contributors.append({
                "factor": "Yawning Deviation",
                "impact": f"+{pts} pts",
                "detail": f"MAR increase Δ: +{deviations['mar_deviation']:.3f} above driver baseline"
            })

        if vision_risk["r_phone"] > 0.3:
            contributors.append({
                "factor": "Possible Phone Usage",
                "impact": "+20 pts",
                "detail": "Phone proximity detected near driver face"
            })

        if vision_risk["r_drink"] > 0.3:
            contributors.append({
                "factor": "Possible Drinking Behavior",
                "impact": "+15 pts",
                "detail": "Drink container proximity detected near driver mouth"
            })

        # Explicitly list missing modalities
        missing_modalities = []
        modality_status = fusion_result["modality_info"]["modality_status"]
        for mod, stat in modality_status.items():
            if stat != "ACTIVE":
                missing_modalities.append(f"{mod.capitalize()} Sensors ({stat})")

        return {
            "score": score,
            "level": level,
            "color": color,
            "contributors": contributors,
            "missing_modalities": missing_modalities,
            "modality_weights": fusion_result["modality_info"]["effective_weights"]
        }
