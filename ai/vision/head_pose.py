import cv2
import numpy as np

class HeadPoseEstimator:
    """
    Head Pose Estimator calculating Pitch, Yaw, and Roll from facial landmarks using cv2.solvePnP.
    Implements EMA angle smoothing to prevent jitter when head rotates.
    """
    def __init__(self, alpha_smooth=0.30, distraction_frames_threshold=18):
        self.alpha_smooth = alpha_smooth
        self.prev_angles = None # np.array([pitch, yaw, roll])
        
        self.model_points = np.array([
            (0.0, 0.0, 0.0),          # Nose tip
            (0.0, -330.0, -65.0),     # Chin
            (-225.0, 170.0, -135.0),  # Left eye corner
            (225.0, 170.0, -135.0),   # Right eye corner
            (-150.0, -150.0, -125.0), # Mouth left corner
            (150.0, -150.0, -125.0)   # Mouth right corner
        ])
        self.distraction_frames_threshold = distraction_frames_threshold
        self.distraction_counter = 0
        self.is_distracted = False

    def update(self, landmarks, image_size):
        w, h = image_size

        # landmarks is now a dict: {left_eye, right_eye, mouth}
        # Derive the 6 PnP anchor points from the eye/mouth arrays
        le  = landmarks["left_eye"]   # shape (6,2)
        re  = landmarks["right_eye"]  # shape (6,2)
        mo  = landmarks["mouth"]      # shape (4,2)

        # Nose tip  ≈ midpoint between eyes, shifted down
        nose_tip   = ((le[0] + re[3]) / 2 + np.array([0, int((le[0][1] + re[3][1]) / 2 * 0.15)]))
        # Chin      ≈ below mouth bottom
        chin       = mo[3] + np.array([0, abs(mo[3][1] - mo[0][1]) * 0.6])
        # Left eye corner, right eye corner
        left_eye_c  = le[0]
        right_eye_c = re[3]
        # Mouth corners
        mouth_l    = mo[0]
        mouth_r    = mo[2]

        image_points = np.array([
            nose_tip, chin, left_eye_c, right_eye_c, mouth_l, mouth_r
        ], dtype="double")

        focal_length = w
        center = (w / 2, h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype="double")

        dist_coeffs = np.zeros((4, 1))
        success, rotation_vector, translation_vector = cv2.solvePnP(
            self.model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not success:
            return {"yaw": 0, "pitch": 0, "roll": 0, "orientation": "LOOKING_FORWARD", "is_distracted": False}

        # Calculate Euler angles
        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        proj_matrix = np.hstack((rotation_matrix, translation_vector))
        _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(proj_matrix)

        raw_pitch, raw_yaw, raw_roll = euler_angles[0][0], euler_angles[1][0], euler_angles[2][0]
        curr_angles = np.array([raw_pitch, raw_yaw, raw_roll], dtype=float)

        # Smooth Angles with Exponential Moving Average
        if self.prev_angles is None:
            smooth_angles = curr_angles
        else:
            smooth_angles = self.alpha_smooth * curr_angles + (1.0 - self.alpha_smooth) * self.prev_angles
        self.prev_angles = smooth_angles

        pitch, yaw, roll = smooth_angles[0], smooth_angles[1], smooth_angles[2]

        # Determine direction
        orientation = "LOOKING_FORWARD"
        if yaw < -18:
            orientation = "LOOKING_RIGHT"
        elif yaw > 18:
            orientation = "LOOKING_LEFT"
        elif pitch < -15:
            orientation = "LOOKING_DOWN"
        elif pitch > 15:
            orientation = "LOOKING_UP"

        if orientation != "LOOKING_FORWARD":
            self.distraction_counter += 1
        else:
            self.distraction_counter = 0

        self.is_distracted = self.distraction_counter >= self.distraction_frames_threshold

        # Posture Status Estimation
        posture_status = "NORMAL"
        posture_confidence = 0.85
        if pitch < -16.0:
            posture_status = "SLOUCHING"
            posture_confidence = 0.80
        elif abs(roll) > 15.0:
            posture_status = "LATERAL_TILT"
            posture_confidence = 0.80

        return {
            "yaw": round(float(yaw), 1),
            "pitch": round(float(pitch), 1),
            "roll": round(float(roll), 1),
            "orientation": orientation,
            "posture_status": posture_status,
            "posture_confidence": posture_confidence,
            "is_distracted": self.is_distracted,
            "distraction_counter": self.distraction_counter
        }
