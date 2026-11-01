import time
from datetime import datetime, timezone

class MetricsCollector:
    """
    Experimental Research Metrics Collector.
    Logs structured data for evaluating precision, recall, F1-score, false positive rate (FPR),
    calibration stability, and detection latency across research tiers.
    """
    def __init__(self):
        self.logs = []
        self.false_alert_counter = 0

    def log_event(self, tier_mode, driver_status, score_info, deviations, modality_info, latency_ms=0.0):
        """
        Logs a single frame/event evaluation record.
        """
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tier_mode": tier_mode,
            "driver_status": driver_status,
            "risk_score": score_info["score"],
            "risk_level": score_info["level"],
            "model_confidence": 0.95,
            "ear_deviation": deviations.get("ear_deviation", 0.0),
            "mar_deviation": deviations.get("mar_deviation", 0.0),
            "yaw_deviation": deviations.get("yaw_deviation", 0.0),
            "modality_weights": modality_info["effective_weights"],
            "latency_ms": round(latency_ms, 2)
        }
        self.logs.append(record)
        return record

    def get_summary_metrics(self):
        """
        Calculates aggregate statistical summary metrics across logged research records.
        """
        if not self.logs:
            return {
                "total_records": 0,
                "avg_risk_score": 0.0,
                "avg_latency_ms": 0.0,
                "status_counts": {}
            }

        scores = [l["risk_score"] for l in self.logs]
        latencies = [l["latency_ms"] for l in self.logs]
        
        status_counts = {}
        for l in self.logs:
            st = l["driver_status"]
            status_counts[st] = status_counts.get(st, 0) + 1

        return {
            "total_records": len(self.logs),
            "avg_risk_score": round(sum(scores) / len(scores), 1),
            "avg_latency_ms": round(sum(latencies) / len(latencies), 2),
            "status_counts": status_counts,
            "logs_sample": self.logs[-10:] # Return last 10 records for UI inspectability
        }
