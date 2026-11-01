"""
SmartRoad AI - Multimodal IoT Sensor Stream Simulator Script
Simulates periodic biometric (Heart Rate, SpO2) and vehicle telemetry (Speed, Acceleration G-force)
payload streams posted to FastAPI endpoint (POST /api/telemetry).
"""

import time
import random
import requests
import argparse
from datetime import datetime, timezone

def run_iot_simulation(api_url="http://127.0.0.1:8000/api", access_token=None, interval_sec=2.0, duration_sec=60):
    print("\n--- SmartRoad AI: Multimodal IoT Sensor Stream Simulator ---")
    print(f"Target API: {api_url}/telemetry")
    print(f"Interval: {interval_sec}s | Duration: {duration_sec}s\n")

    start_time = time.time()
    headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}

    count = 0
    try:
        while time.time() - start_time < duration_sec:
            count += 1
            # Generate realistic sensor values
            simulated_speed = round(random.uniform(55.0, 92.0), 1)
            simulated_hr = random.randint(68, 104)
            simulated_spo2 = random.randint(96, 99)
            simulated_accel = round(random.uniform(0.8, 2.1), 2)
            simulated_alcohol = random.choice([0, 0, 0, 110])
            
            status = "normal"
            if simulated_speed > 85:
                status = "speeding"
            elif simulated_hr > 98:
                status = "drowsy"
            elif simulated_alcohol > 100:
                status = "possible_drinking"

            payload = {
                "speed": simulated_speed,
                "heart_rate": simulated_hr,
                "spo2": simulated_spo2,
                "alcohol_level": simulated_alcohol,
                "acceleration": simulated_accel,
                "latitude": 16.5062,
                "longitude": 80.6480,
                "driver_status": status
            }

            try:
                res = requests.post(f"{api_url}/telemetry", json=payload, headers=headers, timeout=3.0)
                if res.status_code == 201:
                    print(f"[{count}] [POST 201 Created] Speed: {simulated_speed} km/h | HR: {simulated_hr} BPM | SpO2: {simulated_spo2}% | Status: {status.upper()}")
                else:
                    print(f"[{count}] [POST {res.status_code}] Response: {res.text}")
            except Exception as err:
                print(f"[{count}] Connection Error: {err}")

            time.sleep(interval_sec)

    except KeyboardInterrupt:
        print("\n[Simulator] Stopped by user.")

    print(f"\n--- IoT Simulation Complete ({count} records transmitted) ---\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SmartRoad AI Multimodal IoT Stream Simulator")
    parser.add_argument("--url", default="http://127.0.0.1:8000/api", help="FastAPI Base API URL")
    parser.add_argument("--token", default=None, help="JWT Access Token")
    parser.add_argument("--interval", type=float, default=2.0, help="Transmission interval in seconds")
    parser.add_argument("--duration", type=int, default=60, help="Total simulation duration in seconds")

    args = parser.parse_args()
    run_iot_simulation(api_url=args.url, access_token=args.token, interval_sec=args.interval, duration_sec=args.duration)
