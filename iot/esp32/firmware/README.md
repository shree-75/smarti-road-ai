# SmartRoad AI — ESP32 Hardware Firmware & Sensor Wiring Guide

## 1. Hardware Pinout & Wiring

| Sensor / Module | Communication Protocol | ESP32 GPIO Pin | I2C Address / Note |
| :--- | :--- | :--- | :--- |
| **I2C Bus Data (SDA)** | I2C Data | **GPIO 21** | System Master SDA |
| **I2C Bus Clock (SCL)** | I2C Clock | **GPIO 22** | System Master SCL |
| **MAX30102 PPG Sensor** | I2C | SDA 21, SCL 22 | **0x57** (Heart Rate BPM & SpO2 %) |
| **MPU6050 Accel/Gyro** | I2C | SDA 21, SCL 22 | **0x68** (Motion & Impact G-force) |
| **SW-420 Vibration Sensor** | Digital Input | **GPIO 25** | High/Low Impact Trigger |
| **MQ Alcohol Sensor** | Analog Input (ADC) | **GPIO 34** | ADC1_CH6 (0–3.3V Scaled) |

---

## 2. Important Safety Note on MQ Sensor Voltage Scaling

Standard MQ alcohol sensors operate on **5V VCC** and output analog signals up to **5.0V**.  
The ESP32 ADC pins (GPIO 34) accept a **maximum voltage of 3.3V**.

> [!CAUTION]
> Direct connection of a 5V analog signal to ESP32 GPIO 34 will damage the microcontroller pin.
> **Required Circuit**: Insert a 10kΩ / 20kΩ resistor voltage divider on the analog signal wire to scale 5.0V down to 3.3V max:
> `V_esp = V_mq * (20k / (10k + 20k)) = 5.0 * 0.66 = 3.33V`

---

## 3. How to Upload Firmware

### Option A: Arduino IDE
1. Open `smartroad_esp32_firmware.ino` in Arduino IDE.
2. Install libraries: `ArduinoJson` (v6.x or v7.x).
3. Select Board: **ESP32 Dev Module**.
4. Set `WIFI_SSID`, `WIFI_PASS`, and your laptop server IP (`http://<SERVER_IP>:8000/api/v1/iot/telemetry`).
5. Click **Upload** and open Serial Monitor at **115200 baud**.

### Option B: PlatformIO (VS Code)
1. Open `iot/esp32/firmware/` in VS Code with PlatformIO extension.
2. Run `platformio run --target upload`.
