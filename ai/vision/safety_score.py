class SafetyScoreEngine:
    """
    Transparent, explainable Driver Safety Score engine (0 - 100).
    Applies configurable risk deductions based on active behavioral indicators.
    """
    def __init__(self):
        self.base_score = 100

    def compute_score(self, behavioral_state):
        """
        Computes safety score and returns category classification.
        """
        score = 100
        deductions = []

        if behavioral_state.get("face_missing"):
            score -= 40
            deductions.append("Face Not Detected (-40)")

        if behavioral_state.get("is_drowsy"):
            score -= 35
            deductions.append("Drowsiness Detected (-35)")

        if behavioral_state.get("is_distracted"):
            score -= 20
            deductions.append("Driver Distraction (-20)")

        if behavioral_state.get("is_yawning"):
            score -= 10
            deductions.append("Yawning Detected (-10)")

        if behavioral_state.get("possible_phone_use"):
            score -= 25
            deductions.append("Possible Phone Usage (-25)")

        if behavioral_state.get("possible_drinking"):
            score -= 15
            deductions.append("Possible Drinking (-15)")

        final_score = max(0, min(100, score))

        # Risk Classification Categories
        if final_score >= 95:
            category = "Optimal"
        elif final_score >= 70:
            category = "Warning"
        elif final_score >= 40:
            category = "Elevated Risk"
        else:
            category = "Critical Risk"

        return {
            "score": final_score,
            "category": category,
            "deductions": deductions
        }
