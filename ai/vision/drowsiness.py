import numpy as np

def calculate_ear(eye_landmarks):
    """
    Calculates Eye Aspect Ratio (EAR) using standard 6-point landmark geometry.
    Formula:
      EAR = (||p2 - p6|| + ||p3 - p5||) / (2 * ||p1 - p4||)
    """
    p1, p2, p3, p4, p5, p6 = eye_landmarks

    # Vertical distance 1
    v1 = np.linalg.norm(p2 - p6)
    # Vertical distance 2
    v2 = np.linalg.norm(p3 - p5)
    # Horizontal distance
    h = np.linalg.norm(p1 - p4)

    if h == 0:
        return 0.0

    ear = (v1 + v2) / (2.0 * h)
    return float(ear)

class DrowsinessDetector:
    """
    Temporal drowsiness, blink, and PERCLOS eye closure metric detector based on Eye Aspect Ratio (EAR).
    """
    def __init__(self, ear_threshold=0.21, consecutive_frames_threshold=15, perclos_window_size=90):
        self.ear_threshold = ear_threshold
        self.consecutive_frames_threshold = consecutive_frames_threshold
        self.perclos_window_size = perclos_window_size
        self.closed_counter = 0
        self.blink_count = 0
        self.is_drowsy = False
        self.drowsiness_score = 0.0
        self.ear_history = []

    def update(self, left_eye, right_eye):
        left_ear = calculate_ear(left_eye)
        right_ear = calculate_ear(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0

        # Maintain rolling PERCLOS window
        is_closed = avg_ear < self.ear_threshold
        self.ear_history.append(1 if is_closed else 0)
        if len(self.ear_history) > self.perclos_window_size:
            self.ear_history.pop(0)

        # Compute PERCLOS (% of time eyes are closed over rolling window)
        perclos_pct = round((sum(self.ear_history) / len(self.ear_history)) * 100, 1) if self.ear_history else 0.0

        if is_closed:
            self.closed_counter += 1
        else:
            if 2 <= self.closed_counter < self.consecutive_frames_threshold:
                self.blink_count += 1
            self.closed_counter = 0

        # Calculate temporal drowsiness score (0.0 to 1.0)
        self.drowsiness_score = min(1.0, self.closed_counter / (self.consecutive_frames_threshold * 1.5))
        self.is_drowsy = self.closed_counter >= self.consecutive_frames_threshold or perclos_pct >= 40.0

        return {
            "ear": round(avg_ear, 3),
            "left_ear": round(left_ear, 3),
            "right_ear": round(right_ear, 3),
            "perclos_pct": perclos_pct,
            "closed_counter": self.closed_counter,
            "blink_count": self.blink_count,
            "is_drowsy": self.is_drowsy,
            "drowsiness_score": round(self.drowsiness_score, 2),
            "status": "drowsy" if self.is_drowsy else ("blink" if 0 < self.closed_counter < self.consecutive_frames_threshold else "alert")
        }
