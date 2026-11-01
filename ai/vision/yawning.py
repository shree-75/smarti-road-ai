import numpy as np

def calculate_mar(mouth_landmarks):
    """
    Calculates Mouth Aspect Ratio (MAR) using inner mouth landmarks.
    Formula: MAR = ||p_top - p_bottom|| / ||p_left - p_right||
    """
    # p_left (0), p_top (1), p_right (2), p_bottom (3)
    p_left, p_top, p_right, p_bottom = mouth_landmarks[0], mouth_landmarks[1], mouth_landmarks[2], mouth_landmarks[3]

    v = np.linalg.norm(p_top - p_bottom)
    h = np.linalg.norm(p_left - p_right)

    if h == 0:
        return 0.0

    mar = v / h
    return float(mar)

class YawnDetector:
    """
    Temporal yawning detector based on Mouth Aspect Ratio (MAR).
    """
    def __init__(self, mar_threshold=0.55, consecutive_frames_threshold=12):
        self.mar_threshold = mar_threshold
        self.consecutive_frames_threshold = consecutive_frames_threshold
        self.yawn_counter = 0
        self.yawn_count = 0
        self.is_yawning = False

    def update(self, mouth_landmarks):
        mar = calculate_mar(mouth_landmarks)

        if mar > self.mar_threshold:
            self.yawn_counter += 1
        else:
            if self.yawn_counter >= self.consecutive_frames_threshold:
                self.yawn_count += 1
            self.yawn_counter = 0

        self.is_yawning = self.yawn_counter >= self.consecutive_frames_threshold

        return {
            "mar": round(mar, 3),
            "yawn_counter": self.yawn_counter,
            "yawn_count": self.yawn_count,
            "is_yawning": self.is_yawning
        }
