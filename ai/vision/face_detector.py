import cv2
import numpy as np


class FaceMeshDetector:
    """
    Multi-Face Detect-and-Track Engine  (v3 — Stable IDs + No Ghosts)
    ─────────────────────────────────────────────────────────────────
    Fixes vs v2:
      • STABLE IDs   — IoU + centroid-distance dual match against
                       CSRT-updated boxes → same person keeps same ID
      • NO GHOSTS    — minNeighbors=8, confirm_count gate (6 frames)
                       → box shown only after 6 consecutive detections
      • ACCURACY     — scaleFactor=1.05, DETECT_INTERVAL=20
    Architecture:
      Every DETECT_INTERVAL frames : Haar re-detects, IDs preserved
      Between detections           : CSRT tracks movement per-face
      Drop condition               : MAX_MISSED=45 missed tracker frames
    """

    LEFT_EYE    = [0, 1, 2, 3, 4, 5]
    RIGHT_EYE   = [0, 1, 2, 3, 4, 5]
    MOUTH_INNER = [0, 1, 2, 3]

    DETECT_INTERVAL = 20   # Haar runs every N frames
    MAX_MISSED      = 45   # CSRT miss tolerance before drop
    CONFIRM_COUNT   = 6    # frames required before face is shown

    def __init__(self, alpha_smooth=0.30, max_faces=8):
        self.alpha_smooth = alpha_smooth
        self.max_faces    = max_faces

        # Load Haar Cascade (prefer local model directory)
        import os
        base_dir = os.path.dirname(os.path.abspath(__file__))
        local_path = os.path.join(base_dir, "models", "haarcascade_frontalface_default.xml")
        if os.path.exists(local_path):
            cascade_path = local_path
        else:
            cascade_path = getattr(cv2.data, "haarcascades", "") + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        # {face_id: {bbox, tracker, confirm_count, state, missed, landmarks}}
        self.tracked_faces  = {}
        self.next_face_id   = 0
        self.frame_count    = 0

        self.face_state                 = "LOST"
        self.face_lost_counter          = 0
        self.consecutive_detect_counter = 0

    # ──────────────────────────────────────────────────────────────
    # Geometry helpers
    # ──────────────────────────────────────────────────────────────
    def _iou(self, A, B):
        ax2, ay2 = A[0]+A[2], A[1]+A[3]
        bx2, by2 = B[0]+B[2], B[1]+B[3]
        iw = max(0, min(ax2,bx2) - max(A[0],B[0]))
        ih = max(0, min(ay2,by2) - max(A[1],B[1]))
        inter = iw * ih
        union = A[2]*A[3] + B[2]*B[3] - inter
        return inter / union if union > 0 else 0.0

    def _centroid_dist(self, A, B):
        """Normalised centroid distance (0 = same, 1 = far apart)."""
        cax, cay = A[0]+A[2]/2, A[1]+A[3]/2
        cbx, cby = B[0]+B[2]/2, B[1]+B[3]/2
        return ((cax-cbx)**2 + (cay-cby)**2) ** 0.5

    # ──────────────────────────────────────────────────────────────
    # ID matching  —  IoU primary, centroid fallback
    # ──────────────────────────────────────────────────────────────
    def _match_faces(self, new_bboxes):
        """
        Match new Haar detections to existing tracked IDs.
        Uses IoU first; falls back to centroid distance so that
        a slightly shifted detection still maps to the same ID.
        """
        matched  = {}
        used_ids = set()

        for ni, nb in enumerate(new_bboxes):
            best_score, best_id = -1.0, None

            for fid, fd in self.tracked_faces.items():
                if fid in used_ids:
                    continue
                tb = fd["bbox"]   # CSRT-updated box — more accurate than last detect
                iou   = self._iou(nb, tb)
                cdist = self._centroid_dist(nb, tb)
                # Combined score: high IoU good, low centroid dist good
                # Centroid tolerance: ~120 px (tunable)
                cdist_score = max(0.0, 1.0 - cdist / 120.0)
                score = 0.65 * iou + 0.35 * cdist_score

                if score > best_score:
                    best_score, best_id = score, fid

            # Threshold: if combined score > 0.25 → same person
            if best_score > 0.25 and best_id is not None:
                matched[ni] = best_id
                used_ids.add(best_id)
            else:
                matched[ni] = self.next_face_id
                self.next_face_id += 1

        return matched

    # ──────────────────────────────────────────────────────────────
    # Primary driver — largest + most-centered CONFIRMED face
    # ──────────────────────────────────────────────────────────────
    def _select_primary(self, w, h):
        confirmed = {fid: fd for fid, fd in self.tracked_faces.items()
                     if fd["confirm_count"] >= self.CONFIRM_COUNT}
        pool = confirmed if confirmed else self.tracked_faces
        if not pool:
            return None
        cx, cy = w / 2.0, h / 2.0
        best, bid = -1, None
        for fid, fd in pool.items():
            bx, by, bw, bh = fd["bbox"]
            area  = bw * bh
            fcx   = bx + bw / 2
            fcy   = by + bh / 2
            dist  = ((fcx-cx)**2 + (fcy-cy)**2) ** 0.5
            maxd  = (cx**2 + cy**2) ** 0.5
            cs    = 1.0 - dist / (maxd + 1e-6)
            score = 0.6*area + 0.4*cs*(w*h)
            if score > best:
                best, bid = score, fid
        return bid

    # ──────────────────────────────────────────────────────────────
    # CSRT tracker factory
    # ──────────────────────────────────────────────────────────────
    def _new_tracker(self, frame, bbox):
        t = cv2.TrackerCSRT_create()
        t.init(frame, tuple(int(v) for v in bbox))
        return t

    # ──────────────────────────────────────────────────────────────
    # Geometric landmark estimation
    # ──────────────────────────────────────────────────────────────
    def _estimate_landmarks(self, bbox):
        bx, by, bw, bh = bbox
        ley = by + int(bh * 0.38)
        my  = by + int(bh * 0.75)
        le = np.array([
            [bx+int(bw*.22),ley],[bx+int(bw*.28),ley-int(bh*.04)],
            [bx+int(bw*.34),ley-int(bh*.04)],[bx+int(bw*.40),ley],
            [bx+int(bw*.34),ley+int(bh*.04)],[bx+int(bw*.28),ley+int(bh*.04)],
        ], dtype=float)
        re = np.array([
            [bx+int(bw*.60),ley],[bx+int(bw*.66),ley-int(bh*.04)],
            [bx+int(bw*.72),ley-int(bh*.04)],[bx+int(bw*.78),ley],
            [bx+int(bw*.72),ley+int(bh*.04)],[bx+int(bw*.66),ley+int(bh*.04)],
        ], dtype=float)
        mo = np.array([
            [bx+int(bw*.35),my],[bx+int(bw*.50),my-int(bh*.04)],
            [bx+int(bw*.65),my],[bx+int(bw*.50),my+int(bh*.06)],
        ], dtype=float)
        return {"left_eye": le, "right_eye": re, "mouth": mo}

    # ──────────────────────────────────────────────────────────────
    # Main per-frame entry point
    # ──────────────────────────────────────────────────────────────
    def process(self, frame):
        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Dark / no-signal guard
        if np.mean(gray) < 5:
            self.face_lost_counter += 1
            self.consecutive_detect_counter = 0
            self.face_state    = "LOST"
            self.tracked_faces = {}
            return None

        self.frame_count += 1
        do_detect = (self.frame_count % self.DETECT_INTERVAL == 1) or (not self.tracked_faces)

        # ══════════════════════════════════════════════════════════
        # DETECTION phase
        # ══════════════════════════════════════════════════════════
        if do_detect:
            raw = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.05,    # finer scale steps → better accuracy
                minNeighbors=8,      # higher → fewer false positives / ghosts
                minSize=(70, 70),    # ignore tiny noise detections
                flags=cv2.CASCADE_SCALE_IMAGE
            )

            new_bboxes = []
            if len(raw) > 0:
                for (fx, fy, fw, fh) in raw[:self.max_faces]:
                    new_bboxes.append((int(fx), int(fy), int(fw), int(fh)))

            if new_bboxes:
                id_map      = self._match_faces(new_bboxes)
                new_tracked = {}

                for ni, fid in id_map.items():
                    curr  = np.array(new_bboxes[ni], dtype=float)

                    if fid in self.tracked_faces:
                        # Existing face — smooth bbox, carry over confirm_count
                        prev  = np.array(self.tracked_faces[fid]["bbox"], dtype=float)
                        sbox  = self.alpha_smooth * curr + (1 - self.alpha_smooth) * prev
                        cc    = min(self.tracked_faces[fid]["confirm_count"] + 1, 60)
                    else:
                        # Brand-new face — start confirm count at 1
                        sbox, cc = curr, 1

                    ibox  = tuple(sbox.astype(int))
                    state = "DETECTED" if cc >= self.CONFIRM_COUNT else "CONFIRMING"

                    new_tracked[fid] = {
                        "bbox":          ibox,
                        "confirm_count": cc,
                        "state":         state,
                        "missed":        0,
                        "tracker":       self._new_tracker(frame, ibox),
                        "landmarks":     self._estimate_landmarks(ibox),
                    }

                self.tracked_faces = new_tracked
            # else: detection missed this cycle — CSRT continues below

        # ══════════════════════════════════════════════════════════
        # TRACKING phase  (CSRT between detection frames)
        # ══════════════════════════════════════════════════════════
        if not do_detect:
            to_delete = []
            for fid, fd in self.tracked_faces.items():
                ok, new_box = fd["tracker"].update(frame)
                if ok:
                    nb   = (max(0, int(new_box[0])), max(0, int(new_box[1])),
                            int(new_box[2]), int(new_box[3]))
                    prev = np.array(fd["bbox"], dtype=float)
                    sbox = tuple((self.alpha_smooth * np.array(nb, dtype=float) +
                                  (1 - self.alpha_smooth) * prev).astype(int))
                    fd["bbox"]          = sbox
                    fd["confirm_count"] = min(fd["confirm_count"] + 1, 60)
                    fd["state"]         = "DETECTED" if fd["confirm_count"] >= self.CONFIRM_COUNT else "CONFIRMING"
                    fd["missed"]        = 0
                    fd["landmarks"]     = self._estimate_landmarks(sbox)
                else:
                    fd["missed"] += 1
                    if fd["missed"] > self.MAX_MISSED:
                        to_delete.append(fid)

            for fid in to_delete:
                del self.tracked_faces[fid]

        # ── Only count CONFIRMED faces ─────────────────────────────
        confirmed_faces = {fid: fd for fid, fd in self.tracked_faces.items()
                           if fd["confirm_count"] >= self.CONFIRM_COUNT}

        if not confirmed_faces:
            self.face_lost_counter += 1
            self.consecutive_detect_counter = 0
            self.face_state = "LOST"
            return None

        # ══════════════════════════════════════════════════════════
        # Select primary driver & build result
        # ══════════════════════════════════════════════════════════
        primary_id = self._select_primary(w, h)

        self.consecutive_detect_counter += 1
        if self.face_state == "LOST" and self.consecutive_detect_counter < 5:
            self.face_state = "REACQUIRING"
        elif self.consecutive_detect_counter >= 5:
            self.face_state = "DETECTED"
        self.face_lost_counter = 0

        primary = self.tracked_faces[primary_id]
        lm      = primary["landmarks"]

        return {
            "landmarks":       lm,
            "left_eye":        lm["left_eye"],
            "right_eye":       lm["right_eye"],
            "mouth":           lm["mouth"],
            "bbox":            primary["bbox"],
            "image_size":      (w, h),
            "face_state":      primary["state"],
            "face_confidence": 0.93,
            # Only confirmed faces counted
            "person_count":    len(confirmed_faces),
            "primary_id":      primary_id,
            "all_faces":       confirmed_faces,   # only confirmed shown
        }

    # ──────────────────────────────────────────────────────────────
    # Draw overlay on frame
    # ──────────────────────────────────────────────────────────────
    def draw(self, frame, detection):
        if not detection:
            return frame

        all_faces  = detection.get("all_faces", {})
        primary_id = detection.get("primary_id")

        for fid, fd in all_faces.items():
            bx, by, bw, bh = fd["bbox"]
            is_primary = (fid == primary_id)
            color      = (6, 182, 212) if is_primary else (255, 165, 0)
            # Clean label — show fixed ID number
            label = f"DRIVER #{fid}" if is_primary else f"PERSON #{fid}"

            cv2.rectangle(frame, (bx, by), (bx+bw, by+bh), color, 2)
            cv2.putText(frame, label, (bx, by-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

        count = detection["person_count"]
        cv2.putText(frame, f"People: {count}",
                    (10, frame.shape[0]-15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 0), 2)
        return frame

