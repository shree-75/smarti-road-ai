import cv2
import time
import requests
from ai.vision.camera import CameraStream
from ai.pipeline.driver_monitoring_engine import ResearchDriverMonitoringEngine

def run_driver_monitoring(api_url=None, access_token=None, camera_index=0, show_preview=True):
    """
    Main Research Execution Runner for SmartRoad AI.
    Runs local edge camera analysis, 30-sec driver calibration, weighted multimodal risk fusion,
    and posts derived telemetry events to FastAPI.
    """
    camera = CameraStream(camera_index=camera_index, width=640, height=480)
    engine = ResearchDriverMonitoringEngine(calibration_duration_sec=30)
    
    last_api_post_time = 0
    api_post_interval = 2.0

    print("\n--- SmartRoad AI: Personalized Multimodal Driver Risk Monitor Started ---")
    print("Research Focus: Adaptive Driver Calibration & Weighted Multimodal Risk Fusion")
    print("Press 'q' in the camera window to stop.\n")

    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                print("[Runner] Camera frame capture failed.")
                break

            if camera.is_network_stream:
                annotated_frame = frame
            else:
                result = engine.process_frame(frame)
                annotated_frame = result["frame"]

                # Display FPS & Calibration State on preview
                cv2.putText(annotated_frame, f"FPS: {camera.fps:.1f}", (520, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                calib_str = f"CALIB: {result['calibration']['status']}"
                cv2.putText(annotated_frame, calib_str, (20, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 0), 1)

            if show_preview:
                cv2.imshow("SmartRoad AI - Personalized Multimodal Risk Monitor", annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("[Runner] User exit requested.")
                    break

            # Dispatch derived telemetry payload to FastAPI backend
            curr_time = time.time()
            if api_url and access_token and (curr_time - last_api_post_time >= api_post_interval):
                headers = {"Authorization": f"Bearer {access_token}"}
                payload = {
                    "speed": 65.0,
                    "heart_rate": 78,
                    "spo2": 98,
                    "alcohol_level": 0,
                    "acceleration": 1.0,
                    "latitude": 16.5062,
                    "longitude": 80.6480,
                    "driver_status": result["driver_status"]
                }
                try:
                    res = requests.post(f"{api_url}/telemetry", json=payload, headers=headers, timeout=2.0)
                    if res.status_code == 201:
                        print(f"[Runner -> FastAPI] Telemetry Posted: {result['driver_status']} | Score: {result['score_info']['score']}")
                except Exception as err:
                    print(f"[Runner] API dispatch error: {err}")
                
                last_api_post_time = curr_time

    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("--- Driver Risk Monitor Stopped ---")

if __name__ == "__main__":
    run_driver_monitoring()
