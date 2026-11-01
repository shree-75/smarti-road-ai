import cv2
import numpy as np
import time
from ai.pipeline.driver_monitoring_engine import ResearchDriverMonitoringEngine
from ai.vision.camera import CameraStream

def main():
    print("=" * 65)
    print(" SmartRoad AI - Driver Monitoring & Computer Vision Tracker")
    print(" Includes Face Mesh, Hand Tracking, and Mobile Phone Detection")
    print(" (Seatbelt detection feature removed)")
    print("=" * 65)
    print("Starting webcam stream... Press 'q' to quit.")

    camera = CameraStream(camera_index=0, width=640, height=480)
    if not camera.cap:
        print("\n[NOTE] Physical webcam could not be opened directly (likely because backend server is already streaming it).")
        print("You can see the live feed directly on your browser at:")
        print("  -> Dashboard: http://localhost:5173")
        print("  -> Full Camera Stream: http://localhost:8000/api/v1/vision/view\n")

    engine = ResearchDriverMonitoringEngine(calibration_duration_sec=30)

    try:
        while True:
            ret, frame = camera.read()
            if not ret or frame is None:
                time.sleep(0.03)
                continue

            if camera.is_network_stream:
                annotated_frame = frame
            else:
                result = engine.process_frame(frame)
                annotated_frame = result["frame"]

            # Overlay FPS
            fps_val = camera.fps
            cv2.putText(annotated_frame, f"FPS: {fps_val:.1f}", (annotated_frame.shape[1] - 130, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            cv2.imshow("SmartRoad AI - Driver Safety Monitor", annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Exiting...")
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("Camera released and windows closed.")

if __name__ == "__main__":
    main()
