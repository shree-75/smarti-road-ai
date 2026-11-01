import cv2
import time
import platform
import numpy as np

class CameraStream:
    """
    OpenCV Webcam Stream Wrapper with graceful camera index fallback and FPS calculation.
    Supports Windows DirectShow (CAP_DSHOW), Media Foundation (CAP_MSMF), and CAP_ANY.
    Includes consecutive frame drop protection to prevent video stuttering and dropping,
    and optional network stream fallback when the physical webcam is in use by the backend server.
    """
    def __init__(self, camera_index=0, width=640, height=480, allow_network_fallback=True):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.allow_network_fallback = allow_network_fallback
        self.cap = None
        self.is_network_stream = False
        self.prev_time = time.time()
        self.fps = 0.0
        self._last_reconnect_time = 0.0
        self._consecutive_failures = 0
        self._last_good_frame = None

        self._init_camera()

    def _init_camera(self):
        # On Windows, DirectShow and MSMF are tried
        if platform.system() == "Windows":
            backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        else:
            backends = [cv2.CAP_ANY]

        # Deduplicate camera indices
        indices = []
        for idx in [self.camera_index, 0, 1, 2]:
            if idx not in indices:
                indices.append(idx)

        for backend in backends:
            for index in indices:
                try:
                    cap = cv2.VideoCapture(index, backend)
                    if cap.isOpened():
                        # Set resolution & FPS BEFORE reading warmup frames
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                        cap.set(cv2.CAP_PROP_FPS, 30)

                        # Warm up sensor by reading up to 5 frames
                        for _ in range(5):
                            ret, frame = cap.read()
                            if ret and frame is not None and frame.size > 0:
                                self.cap = cap
                                self.camera_index = index
                                self.is_network_stream = False
                                self._consecutive_failures = 0
                                print(f"[CameraStream] Successfully initialized webcam at index {self.camera_index} (backend: {backend})")
                                return
                            time.sleep(0.04)
                        cap.release()
                except Exception:
                    pass

        # If physical webcam could not be opened and network fallback is permitted,
        # check if local FastAPI backend server is already streaming it
        if self.allow_network_fallback:
            try:
                stream_url = "http://127.0.0.1:8000/api/v1/vision/stream"
                stream_cap = cv2.VideoCapture(stream_url)
                if stream_cap.isOpened():
                    for _ in range(3):
                        ret, frame = stream_cap.read()
                        if ret and frame is not None and frame.size > 0:
                            self.cap = stream_cap
                            self.is_network_stream = True
                            self._consecutive_failures = 0
                            print(f"[CameraStream] Attached to active backend camera stream ({stream_url})")
                            return
                        time.sleep(0.05)
                    stream_cap.release()
            except Exception:
                pass

        # If not opened, leave self.cap = None for read() to attempt auto-reconnection
        self.cap = None

    def read(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret and frame is not None and frame.size > 0:
                self._consecutive_failures = 0
                self._last_good_frame = frame
                curr_time = time.time()
                time_diff = curr_time - self.prev_time
                if time_diff > 0:
                    self.fps = 0.9 * self.fps + 0.1 * (1.0 / time_diff)
                self.prev_time = curr_time
                return True, frame
            else:
                self._consecutive_failures += 1
                # If only 1-15 frames dropped momentarily, return the last good frame smoothly
                if self._consecutive_failures < 15 and self._last_good_frame is not None:
                    return True, self._last_good_frame

                # Sustained failure: release device handle
                try:
                    self.cap.release()
                except Exception:
                    pass
                self.cap = None

        # Auto-reconnection attempt every 1.5 seconds if hardware was busy
        curr_time = time.time()
        if curr_time - self._last_reconnect_time > 1.5:
            self._last_reconnect_time = curr_time
            self._init_camera()
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None and frame.size > 0:
                    self._consecutive_failures = 0
                    self._last_good_frame = frame
                    return True, frame

        # Graceful fallback frame while waiting for camera
        fallback = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        cv2.putText(fallback, "INITIALIZING WEBCAM STREAM...", (75, 230),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 215, 255), 2)
        cv2.putText(fallback, "Searching for connected camera device", (95, 270),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (160, 160, 160), 1)
        self.fps = 5.0
        return True, fallback

    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
            print("[CameraStream] Camera device released.")
