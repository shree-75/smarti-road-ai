import os
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class ObjectDetector:
    """
    Computer Vision Object & Hand Tracking Detector.
    Uses Google MediaPipe EfficientDet-Lite0 for 'cell phone', 'bottle', 'cup' object detection,
    and MediaPipe HandLandmarker for comprehensive hand detection and tracking.
    Accurately distinguishes between a bare hand near the ear and an actual phone call.
    """
    def __init__(self, temporal_threshold_frames=2):
        self.temporal_threshold = temporal_threshold_frames
        self.phone_frames = 0
        self.drinking_frames = 0
        self.last_active_phone_boxes = []
        self.last_phone_reason = ""
        self.last_phone_conf = 0.0

        self.supported_classes = ["person", "cell phone", "bottle", "cup"]

        # Models Path
        base_dir = os.path.dirname(os.path.abspath(__file__))
        obj_model_path = os.path.join(base_dir, "models", "efficientdet_lite0.tflite")
        hand_model_path = os.path.join(base_dir, "models", "hand_landmarker.task")

        self.obj_detector = None
        self.hand_detector = None

        # Initialize Object Detector (Optimized score threshold & max_results)
        if os.path.exists(obj_model_path):
            try:
                base_options = python.BaseOptions(model_asset_path=obj_model_path)
                options = vision.ObjectDetectorOptions(
                    base_options=base_options, 
                    score_threshold=0.18,
                    max_results=20
                )
                self.obj_detector = vision.ObjectDetector.create_from_options(options)
            except Exception as e:
                print(f"[ObjectDetector] Warning: Could not init EfficientDet: {e}")

        # Initialize Hand Detector (tracks up to 2 hands)
        if os.path.exists(hand_model_path):
            try:
                hand_options = python.BaseOptions(model_asset_path=hand_model_path)
                hand_det_opts = vision.HandLandmarkerOptions(
                    base_options=hand_options, 
                    num_hands=2,
                    min_hand_detection_confidence=0.3,
                    min_hand_presence_confidence=0.3
                )
                self.hand_detector = vision.HandLandmarker.create_from_options(hand_det_opts)
            except Exception as e:
                print(f"[ObjectDetector] Warning: Could not init HandLandmarker: {e}")

    def update(self, frame, face_detection=None):
        """
        Runs object detection and hand position analysis to detect:
        1. Hands tracking (landmarks, bounding boxes, handedness)
        2. Real cell phone detection (in hand, in frame, or at ear during calls)
        3. Drinking beverage bottles / cups
        """
        h, w, _ = frame.shape
        mp_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=mp_rgb)

        raw_phone_found = False
        raw_drinking_found = False
        detected_phone_boxes = []
        phone_reason = ""
        phone_conf = 0.0

        # ─────────────────────────────────────────────────────────────
        # 1. Hand Tracking Analysis (MediaPipe HandLandmarker)
        # ─────────────────────────────────────────────────────────────
        detected_hands = []
        if self.hand_detector:
            try:
                hand_result = self.hand_detector.detect(mp_image)
                if hand_result.hand_landmarks:
                    for idx, hand_lms in enumerate(hand_result.hand_landmarks):
                        handedness_label = "Hand"
                        hand_score = 0.85
                        if hand_result.handedness and idx < len(hand_result.handedness):
                            cats = hand_result.handedness[idx]
                            if cats:
                                handedness_label = cats[0].category_name
                                hand_score = float(cats[0].score)

                        lms_px = [(int(lm.x * w), int(lm.y * h)) for lm in hand_lms]
                        xs = [p[0] for p in lms_px]
                        ys = [p[1] for p in lms_px]
                        min_x = max(0, min(xs) - 15)
                        max_x = min(w, max(xs) + 15)
                        min_y = max(0, min(ys) - 15)
                        max_y = min(h, max(ys) + 15)

                        detected_hands.append({
                            "bbox": (min_x, min_y, max_x - min_x, max_y - min_y),
                            "handedness": handedness_label,
                            "landmarks": lms_px,
                            "wrist": lms_px[0],
                            "index_tip": lms_px[8],
                            "score": hand_score
                        })
            except Exception as e:
                pass

        # ─────────────────────────────────────────────────────────────
        # 2. Google MediaPipe EfficientDet Object Detection
        # ─────────────────────────────────────────────────────────────
        if self.obj_detector:
            try:
                detection_result = self.obj_detector.detect(mp_image)
                for det in detection_result.detections:
                    for category in det.categories:
                        cat_name = category.category_name.lower()
                        score = float(category.score)
                        bbox = det.bounding_box
                        
                        bx = max(0, int(bbox.origin_x))
                        by = max(0, int(bbox.origin_y))
                        bw = int(bbox.width)
                        bh = int(bbox.height)

                        if cat_name in ["cell phone", "mobile phone", "phone"] and score >= 0.18:
                            raw_phone_found = True
                            phone_conf = max(phone_conf, score)
                            detected_phone_boxes.append({
                                "bbox": (bx, by, bw, bh),
                                "label": f"PHONE: {int(score * 100)}%",
                                "confidence": score
                            })
                            phone_reason = "PHONE IN FRAME"

                        elif cat_name in ["bottle", "cup"] and score >= 0.25:
                            raw_drinking_found = True
            except Exception as e:
                pass

        # ─────────────────────────────────────────────────────────────
        # 3. Contextual Ear Proximity & Gesture Analysis
        # ─────────────────────────────────────────────────────────────
        hand_near_ear = False
        phone_near_ear = False

        if face_detection and "bbox" in face_detection:
            fx, fy, fw, fh = face_detection["bbox"]
            left_ear_x = max(0, fx - int(fw * 0.25))
            left_ear_y = fy + int(fh * 0.45)
            right_ear_x = min(w, fx + int(fw * 1.25))
            right_ear_y = fy + int(fh * 0.45)
            ear_proximity_dist = fw * 0.75

            # Check if any detected hand is near an ear
            for hand in detected_hands:
                hx, hy = hand["index_tip"]
                wx, wy = hand["wrist"]
                d_left = min(np.hypot(hx - left_ear_x, hy - left_ear_y), np.hypot(wx - left_ear_x, wy - left_ear_y))
                d_right = min(np.hypot(hx - right_ear_x, hy - right_ear_y), np.hypot(wx - right_ear_x, wy - right_ear_y))
                if d_left < ear_proximity_dist or d_right < ear_proximity_dist:
                    hand_near_ear = True
                    break

            # Check if any detected phone is near an ear
            for pbox in detected_phone_boxes:
                px, py, pw, ph = pbox["bbox"]
                pc_x = px + pw / 2.0
                pc_y = py + ph / 2.0
                d_left = np.hypot(pc_x - left_ear_x, pc_y - left_ear_y)
                d_right = np.hypot(pc_x - right_ear_x, pc_y - right_ear_y)
                if d_left < ear_proximity_dist * 1.3 or d_right < ear_proximity_dist * 1.3:
                    phone_near_ear = True
                    break

            # Distinguish Phone Call vs Bare Hand Touching Ear:
            # ONLY flag PHONE CALL if a phone object is ACTUALLY present!
            if phone_near_ear:
                raw_phone_found = True
                phone_conf = max(phone_conf, 0.90)
                phone_reason = "PHONE CALL (PHONE AT EAR)"
            elif raw_phone_found and hand_near_ear:
                phone_conf = max(phone_conf, 0.88)
                phone_reason = "PHONE CALL (HAND + PHONE AT EAR)"
            elif raw_phone_found:
                # Check if phone is in hand
                phone_in_hand = False
                for hand in detected_hands:
                    hx, hy, hw, hh = hand["bbox"]
                    for pbox in detected_phone_boxes:
                        px, py, pw, ph = pbox["bbox"]
                        # Bounding box intersection check
                        if not (px + pw < hx or px > hx + hw or py + ph < hy or py > hy + hh):
                            phone_in_hand = True
                            break
                if phone_in_hand:
                    phone_reason = "PHONE IN HAND (BROWSING / TEXTING)"
                else:
                    phone_reason = "PHONE DETECTED"

        # ─────────────────────────────────────────────────────────────
        # 4. Temporal Smoothing for Phone
        # ─────────────────────────────────────────────────────────────
        if raw_phone_found:
            self.phone_frames = min(12, self.phone_frames + 2)
            self.last_active_phone_boxes = detected_phone_boxes
            self.last_phone_reason = phone_reason
            self.last_phone_conf = phone_conf
        else:
            self.phone_frames = max(0, self.phone_frames - 1)

        is_phone_active = self.phone_frames >= self.temporal_threshold

        if is_phone_active:
            phone_status = f"PHONE: DETECTED ({self.last_phone_reason or 'ACTIVE'})"
            active_phone_boxes = detected_phone_boxes if raw_phone_found else self.last_active_phone_boxes
            active_conf = max(phone_conf, self.last_phone_conf, 0.80)
            active_reason = self.last_phone_reason or "PHONE IN USE"
        else:
            phone_status = "PHONE: NOT IN USE"
            active_phone_boxes = []
            active_conf = 0.0
            active_reason = ""

        # ─────────────────────────────────────────────────────────────
        # 5. Temporal Smoothing for Drinking
        # ─────────────────────────────────────────────────────────────
        if raw_drinking_found:
            self.drinking_frames = min(15, self.drinking_frames + 1)
        else:
            self.drinking_frames = max(0, self.drinking_frames - 1)

        is_drinking_active = self.drinking_frames >= self.temporal_threshold
        drinking_status = "DRINKING: DETECTED" if is_drinking_active else "DRINKING: NOT DETECTED"

        return {
            "possible_phone_detected": is_phone_active,
            "phone_status": phone_status,
            "phone_confidence": active_conf,
            "phone_reason": active_reason,
            "phone_boxes": active_phone_boxes,
            "hands_detected": len(detected_hands) > 0,
            "hand_count": len(detected_hands),
            "detected_hands": detected_hands,
            "hand_near_ear": hand_near_ear,
            "possible_drinking_detected": is_drinking_active,
            "drinking_status": drinking_status,
            "drinking_confidence": 0.80 if is_drinking_active else 0.0,
            "supported_classes": self.supported_classes
        }
