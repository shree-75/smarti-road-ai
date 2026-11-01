import os
import sys
import time
import threading
from fastapi import APIRouter
from fastapi.responses import StreamingResponse, HTMLResponse

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except Exception as _cv_err:
    cv2 = None
    np = None
    HAS_CV2 = False
    print(f"[Vision Module Note] Running in cloud mode without OpenCV: {_cv_err}")

# Add project root dynamically so ai.* imports work from backend context
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Ensure stdout/stderr handles UTF-8 safely on Windows
try:
    if sys.stdout:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if sys.stderr:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

try:
    from ai.vision.camera import CameraStream
    from ai.pipeline.driver_monitoring_engine import ResearchDriverMonitoringEngine
    HAS_AI_MODULES = True
except Exception as _ai_err:
    HAS_AI_MODULES = False
    CameraStream = None
    ResearchDriverMonitoringEngine = None
    print(f"[Vision Module Note] Running in headless mode: {_ai_err}")

router = APIRouter(prefix="/vision", tags=["Vision Streaming"])

# ─────────────────────────────────────────────────────────────
# Singleton camera engine — shared across all browser clients
# ─────────────────────────────────────────────────────────────
class _CameraEngine:
    def __init__(self):
        self._camera  = None
        self._engine  = None
        self._lock    = threading.Lock()
        self._running = False
        self._latest_frame: bytes = b""

        # Automated Emergency Trigger State
        self._two_hands_frames = 0
        self._hands_missing_frames = 0
        self._phone_in_use_frames = 0
        self._last_call_time = 0.0
        self._call_cooldown = 90.0  # 90-second cooldown between calls to prevent spamming
        self._last_call_reason = ""
        self._last_call_result = {}

        self._latest_metrics: dict = {
            "active": False,
            "person_count": 1,
            "face_detected": True,
            "driver_status": "normal",
            "hands_detected": False,
            "hand_count": 0,
            "two_hands_detected": False,
            "two_hands_sec": 0.0,
            "hand_near_ear": False,
            "phone_detected": False,
            "phone_status": "PHONE: NOT IN USE",
            "phone_reason": "",
            "phone_confidence": 0.0,
            "calling_detected": False,
            "drinking_detected": False,
            "drinking_status": "DRINKING: NOT DETECTED",
            "ear": 0.292,
            "left_ear": 0.290,
            "right_ear": 0.294,
            "mar": 0.185,
            "yaw": 0.0,
            "pitch": 0.0,
            "roll": 0.0,
            "head_orientation": "LOOKING_FORWARD",
            "posture_status": "NORMAL",
            "risk_score": 18,
            "risk_level": "LOW",
            "fps": 0.0,
            "hands_missing_sec": 0.0,
            "phone_in_use_sec": 0.0,
            "emergency_call_recent": False,
            "emergency_call_reason": "",
            "emergency_call_status": "IDLE",
            "emergency_call_message": "",
            "emergency_call_cooldown_remaining": 0
        }
        self._thread  = None

    def start(self):
        with self._lock:
            if self._running:
                return
            self._running = True
            self._thread  = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()
            print("[CameraEngine] Background vision thread started.")

    def stop(self):
        with self._lock:
            self._running = False
            if self._camera:
                try:
                    self._camera.release()
                except Exception:
                    pass
                self._camera = None

    def _trigger_call_async(self, reason: str):
        """Dispatches Twilio Voice Call & SMS in background to default +919704638232 without stalling camera stream."""
        try:
            # Play audible alert sound on host PC
            try:
                import winsound
                winsound.Beep(1200, 250)
                winsound.Beep(1800, 350)
            except Exception:
                pass

            auto_call = os.getenv("ENABLE_EMERGENCY_AUTO_CALL", "true").lower() in ("true", "1", "yes")
            if not auto_call:
                print(f"[Emergency Call Engine] Auto-call suppressed by ENABLE_EMERGENCY_AUTO_CALL=false: {reason}")
                self._last_call_result = {"status": "MUTED", "message": f"Auto-call disabled via configuration ({reason})"}
                return

            from app.services.twilio_service import make_emergency_call, send_emergency_sms
            print(f"\n[Emergency Call Engine] AUTOMATED TRIGGER ACTIVATED: {reason}")
            res = make_emergency_call(to_phone="+919704638232", reason=reason)
            send_emergency_sms(f"SMARTROAD AI EMERGENCY! {reason}. Immediate driver attention required.", recipient_phone="+919704638232")
            self._last_call_result = res
            print(f"[Emergency Call Engine Result] {res}")
        except Exception as e:
            print(f"[Emergency Call Engine Error] {e}")
            self._last_call_result = {"status": "FAILED", "message": str(e)}

    def _loop(self):
        if not HAS_CV2 or not HAS_AI_MODULES or CameraStream is None:
            print("[CameraEngine] Cloud/Headless deployment detected. Local AI camera hardware loop disabled.")
            while self._running:
                time.sleep(1.0)
            return

        try:
            self._camera = CameraStream(camera_index=0, width=640, height=480, allow_network_fallback=False)
            self._engine = ResearchDriverMonitoringEngine(calibration_duration_sec=30)
            print("[CameraEngine] Webcam and AI pipeline initialized successfully.")
        except Exception as e:
            print(f"[CameraEngine] Pipeline initialization error: {e}")
            self._running = False
            return

        while self._running:
            if not self._camera:
                time.sleep(0.1)
                continue

            ret, frame = self._camera.read()
            if not ret:
                time.sleep(0.04)
                continue

            try:
                result = self._engine.process_frame(frame)
                annotated = result["frame"]

                fps_val = float(self._camera.fps) if self._camera else 0.0
                fps_text = f"FPS: {fps_val:.1f}"
                cv2.putText(annotated, fps_text, (annotated.shape[1] - 130, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                count = result.get("person_count", 0)
                cv2.putText(annotated, f"People: {count}",
                            (10, annotated.shape[0] - 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                m = result.get("metrics", {})
                s = result.get("score_info", {})
                
                phone_detected = bool(m.get("phone_detected", False))
                phone_status = str(m.get("phone_status", "PHONE: NOT IN USE"))
                phone_reason = str(m.get("phone_reason", ""))
                calling_detected = "CALL" in phone_reason or "EAR" in phone_reason

                hands_detected = bool(m.get("hands_detected", False))
                hand_count = int(m.get("hand_count", 0))
                face_present = bool(result.get("face_detected", False)) or count > 0

                # ─────────────────────────────────────────────────────────────
                # Automated Emergency Call Triggers:
                # 1. Two hands detected (hand_count >= 2: hands raised/gesturing off wheel)
                # 2. Driver leaves both hands off steering wheel (hand_count == 0 when face present)
                # 3. Mobile phone detected or in use (phone_detected or calling_detected)
                # ─────────────────────────────────────────────────────────────
                if hand_count >= 2:
                    self._two_hands_frames += 1
                else:
                    self._two_hands_frames = max(0, self._two_hands_frames - 2)

                if face_present and hand_count == 0:
                    self._hands_missing_frames += 1
                else:
                    self._hands_missing_frames = max(0, self._hands_missing_frames - 2)

                if phone_detected or calling_detected:
                    self._phone_in_use_frames += 1
                else:
                    self._phone_in_use_frames = max(0, self._phone_in_use_frames - 2)

                # Intelligent frame thresholds (~2.5s to 5.0s at 15 FPS)
                TRIGGER_FRAMES_PHONE = 40       # ~2.6s of continuous phone usage
                TRIGGER_FRAMES_TWO_HANDS = 40    # ~2.6s of both hands gesturing/raised
                TRIGGER_FRAMES_HANDS_OFF = 75    # ~5.0s of sustained missing hands from steering area

                curr_time = time.time()
                trigger_reason = None

                if self._phone_in_use_frames >= TRIGGER_FRAMES_PHONE:
                    trigger_reason = "Driver is using a mobile phone while driving"
                elif self._two_hands_frames >= TRIGGER_FRAMES_TWO_HANDS:
                    trigger_reason = "Both hands detected off steering wheel (two hands raised/gesturing)"
                elif self._hands_missing_frames >= TRIGGER_FRAMES_HANDS_OFF:
                    trigger_reason = "Driver has removed both hands from the steering wheel"

                if trigger_reason and (curr_time - self._last_call_time >= self._call_cooldown):
                    self._last_call_time = curr_time
                    self._last_call_reason = trigger_reason
                    threading.Thread(target=self._trigger_call_async, args=(trigger_reason,), daemon=True).start()

                two_hands_sec = round(self._two_hands_frames / 15.0, 1)
                hands_missing_sec = round(self._hands_missing_frames / 15.0, 1)
                phone_in_use_sec = round(self._phone_in_use_frames / 15.0, 1)

                # Visual Warning Overlays on Frame
                y_pos = 200
                if self._two_hands_frames >= 10:
                    cv2.putText(annotated, f"WARNING: 2 HANDS DETECTED ({two_hands_sec}s / 2.6s)",
                                (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
                    y_pos += 25
                if self._hands_missing_frames >= 15:
                    cv2.putText(annotated, f"WARNING: BOTH HANDS OFF ({hands_missing_sec}s / 5.0s)",
                                (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
                    y_pos += 25
                if self._phone_in_use_frames >= 10:
                    cv2.putText(annotated, f"WARNING: PHONE IN USE ({phone_in_use_sec}s / 2.6s)",
                                (20, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
                    y_pos += 25

                if (curr_time - self._last_call_time) < 14.0:
                    c_status = self._last_call_result.get("status", "DISPATCHED")
                    call_msg = f"EMERGENCY CALL: {c_status} -> +919704638232"
                    cv2.rectangle(annotated, (15, y_pos - 18), (min(annotated.shape[1] - 15, 620), y_pos + 10), (0, 0, 180), -1)
                    cv2.putText(annotated, call_msg,
                                (22, y_pos - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

                metrics_snapshot = {
                    "active": True,
                    "person_count": count,
                    "face_detected": bool(result.get("face_detected", False)),
                    "driver_status": str(result.get("driver_status", "normal")),
                    "hands_detected": hands_detected,
                    "hand_count": hand_count,
                    "two_hands_detected": bool(hand_count >= 2),
                    "two_hands_sec": two_hands_sec,
                    "hand_near_ear": bool(m.get("hand_near_ear", False)),
                    "phone_detected": phone_detected,
                    "phone_status": phone_status,
                    "phone_reason": phone_reason,
                    "phone_confidence": float(m.get("phone_confidence", 0.0)),
                    "calling_detected": calling_detected,
                    "drinking_detected": bool(m.get("drinking_detected", False)),
                    "drinking_status": str(m.get("drinking_status", "DRINKING: NOT DETECTED")),
                    "ear": round(float(m.get("ear", 0.29)), 3),
                    "left_ear": round(float(m.get("left_ear", 0.29)), 3),
                    "right_ear": round(float(m.get("right_ear", 0.29)), 3),
                    "mar": round(float(m.get("mar", 0.18)), 3),
                    "yaw": round(float(m.get("yaw", 0.0)), 1),
                    "pitch": round(float(m.get("pitch", 0.0)), 1),
                    "roll": round(float(m.get("roll", 0.0)), 1),
                    "head_orientation": str(m.get("head_orientation", "LOOKING_FORWARD")),
                    "posture_status": str(m.get("posture_status", "NORMAL")),
                    "risk_score": int(s.get("score", 18)),
                    "risk_level": str(s.get("level", "LOW")),
                    "fps": round(fps_val, 1),
                    "hands_missing_sec": hands_missing_sec,
                    "phone_in_use_sec": phone_in_use_sec,
                    "emergency_call_recent": bool((curr_time - self._last_call_time) < 15.0),
                    "emergency_call_reason": self._last_call_reason,
                    "emergency_call_status": self._last_call_result.get("status", "IDLE"),
                    "emergency_call_message": self._last_call_result.get("message", ""),
                    "emergency_call_cooldown_remaining": max(0, int(self._call_cooldown - (curr_time - self._last_call_time)))
                }

            except Exception as e:
                import traceback
                print(f"[VisionEngine Error] {e}")
                traceback.print_exc()
                annotated = frame
                metrics_snapshot = self._latest_metrics

            _, jpeg = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 80])
            with self._lock:
                self._latest_frame = jpeg.tobytes()
                self._latest_metrics = metrics_snapshot

    def get_frame(self) -> bytes:
        with self._lock:
            return self._latest_frame

    def get_metrics(self) -> dict:
        with self._lock:
            return dict(self._latest_metrics)


_engine = _CameraEngine()


# ─────────────────────────────────────────────────────────────
# MJPEG generator
# ─────────────────────────────────────────────────────────────
def _mjpeg_generator():
    if not _engine._running:
        _engine.start()
    boundary = b"--frame"
    while True:
        frame = _engine.get_frame()
        if frame:
            yield (
                boundary + b"\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: " + str(len(frame)).encode() + b"\r\n\r\n"
                + frame + b"\r\n"
            )
        time.sleep(0.033)   # ~30 fps cap


# ─────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────
@router.get("/stream")
def video_stream():
    """MJPEG live camera stream with face, hands, and object tracking overlay."""
    return StreamingResponse(
        _mjpeg_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@router.get("/metrics")
def camera_metrics():
    """Live computer vision telemetry metrics JSON with automated call triggers."""
    if not _engine._running:
        _engine.start()
    return _engine.get_metrics()


@router.get("/status")
def camera_status():
    """Returns camera streaming status."""
    return {
        "status": "online" if _engine._running else "idle",
        "active": _engine._running,
        "fps": getattr(_engine._camera, "fps", 0.0) if _engine._camera else 0.0,
        "view_url": "/api/v1/vision/view",
        "stream_url": "/api/v1/vision/stream",
        "metrics_url": "/api/v1/vision/metrics"
    }


@router.get("/view", response_class=HTMLResponse)
def camera_view():
    """Browser-friendly page showing the live tracking feed."""
    html = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>SmartRoad AI — Live Face & Hand Tracker</title>
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body {
      background: #0f172a;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      font-family: 'Segoe UI', sans-serif;
      color: #e2e8f0;
    }
    h1 {
      font-size: 1.5rem;
      margin-bottom: 1rem;
      color: #06b6d4;
      letter-spacing: 0.1em;
    }
    .badge {
      display: inline-block;
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 999px;
      padding: 4px 14px;
      font-size: 0.75rem;
      margin-bottom: 1.2rem;
      color: #94a3b8;
    }
    img {
      border-radius: 12px;
      border: 2px solid #06b6d4;
      max-width: 95vw;
      box-shadow: 0 0 40px rgba(6,182,212,0.25);
    }
    .legend {
      margin-top: 1rem;
      display: flex;
      gap: 24px;
      font-size: 0.82rem;
    }
    .legend span { display:flex; align-items:center; gap:6px; }
    .dot { width:12px; height:12px; border-radius:3px; }
    .cyan  { background:#06b6d4; }
    .green { background:#10b981; }
    .red   { background:#ef4444; }
  </style>
</head>
<body>
  <h1>🚗 SmartRoad AI — Live Face, Hand & Phone Tracker</h1>
  <div class="badge">MJPEG · Real-time · Face Mesh + Hand Tracking + Phone Detection</div>
  <img src="/api/v1/vision/stream" alt="Live camera feed" />
  <div class="legend">
    <span><div class="dot cyan"></div> Driver Face Mesh</span>
    <span><div class="dot green"></div> Hand Tracking Skeleton</span>
    <span><div class="dot red"></div> Mobile Phone Box</span>
  </div>
</body>
</html>
"""
    return HTMLResponse(content=html)
