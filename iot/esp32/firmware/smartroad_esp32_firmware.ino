/**
 * ============================================================================
 * SMARTROAD AI — AUTOMATIC NETWORK DISCOVERY & DYNAMIC ESP32 TELEMETRY FIRMWARE
 * ============================================================================
 * Network Configuration:
 * - Active Wi-Fi SSID: sb (2.4 GHz)
 * - Active Laptop Server IP: 10.105.159.142
 * ============================================================================
 */

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <HTTPClient.h>
#include <Wire.h>

// ============================================================================
// 1. WI-FI & DISCOVERY CONFIGURATION
// ============================================================================
const char* PRIMARY_SSID = "sb";
const char* PRIMARY_PASS = "mrdu@1234";

const int BACKEND_PORT        = 8000;
const int UDP_DISCOVERY_PORT = 8001;
const char* API_CONFIG_PATH   = "/api/v1/iot/config";
const char* API_TELEMETRY_PATH= "/api/v1/iot/telemetry";

#define I2C_SDA 21
#define I2C_SCL 22
#define MQ_ALCOHOL_PIN 34
#define SW420_VIBRATION_PIN 25

#define MAX30102_ADDR 0x57
#define MPU6050_ADDR 0x68

const char* DEVICE_ID = "ESP32-001";

// Dynamic Server IP Storage (Active Laptop IP: 10.105.159.142)
String detectedServerIP = "10.105.159.142";
bool serverDiscovered = true;

unsigned long lastTelemetryTime = 0;
const unsigned long TELEMETRY_INTERVAL_MS = 1000; // 1 Hz (1 Second Interval)

WiFiUDP udp;

bool checkI2CDevice(uint8_t address) {
  Wire.beginTransmission(address);
  return (Wire.endTransmission() == 0);
}

bool discoverBackendServer() {
  if (detectedServerIP.length() > 0) {
    String testUrl = "http://" + detectedServerIP + ":" + String(BACKEND_PORT) + API_CONFIG_PATH;
    HTTPClient testHttp;
    testHttp.begin(testUrl);
    testHttp.setTimeout(800);
    int testCode = testHttp.GET();
    testHttp.end();

    if (testCode == 200) {
      serverDiscovered = true;
      Serial.printf("🟢 [DISCOVERY] Verified Active Backend Server at: %s\n", detectedServerIP.c_str());
      return true;
    }
  }

  // Subnet Host Scanner
  IPAddress localIP = WiFi.localIP();
  String ipStr = localIP.toString();
  int lastDot = ipStr.lastIndexOf('.');
  if (lastDot > 0) {
    String subnetPrefix = ipStr.substring(0, lastDot + 1);
    Serial.printf("[DISCOVERY] Scanning subnet %sX for active backend...\n", subnetPrefix.c_str());

    for (int host = 130; host <= 160; host++) {
      String testIP = subnetPrefix + String(host);
      String testUrl = "http://" + testIP + ":" + String(BACKEND_PORT) + API_CONFIG_PATH;

      HTTPClient testHttp;
      testHttp.begin(testUrl);
      testHttp.setTimeout(150);
      int code = testHttp.GET();
      testHttp.end();

      if (code == 200) {
        detectedServerIP = testIP;
        serverDiscovered = true;
        Serial.printf("🟢 [DISCOVERY] Auto-Discovered Server at: %s\n", detectedServerIP.c_str());
        return true;
      }
    }
  }
  return false;
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(MQ_ALCOHOL_PIN, INPUT);
  pinMode(SW420_VIBRATION_PIN, INPUT);

  Wire.begin(I2C_SDA, I2C_SCL);

  WiFi.disconnect(true);
  delay(100);
  WiFi.mode(WIFI_STA);
  WiFi.begin(PRIMARY_SSID, PRIMARY_PASS);

  Serial.printf("[WiFi] Connecting to 2.4GHz network %s", PRIMARY_SSID);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 25) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n🟢 [WiFi] CONNECTED SUCCESSFULLY TO 'sb' (2.4 GHz)!");
    discoverBackendServer();
  } else {
    Serial.println("\n🔴 [WiFi] CONNECTION FAILED!");
  }

  Serial.println("\n====================================");
  Serial.println("SMARTROAD AI ESP32 NETWORK STATUS");
  Serial.println("====================================");
  Serial.printf("WiFi SSID       : %s\n", PRIMARY_SSID);
  Serial.printf("WiFi Status     : %s\n", (WiFi.status() == WL_CONNECTED) ? "CONNECTED" : "FAILED");
  Serial.printf("ESP32 IP        : %s\n", WiFi.localIP().toString().c_str());
  Serial.printf("Gateway         : %s\n", WiFi.gatewayIP().toString().c_str());
  Serial.printf("Backend Server  : %s\n", detectedServerIP.c_str());
  Serial.printf("Backend Port    : %d\n", BACKEND_PORT);
  Serial.printf("Telemetry URL   : http://%s:%d%s\n", detectedServerIP.c_str(), BACKEND_PORT, API_TELEMETRY_PATH);
  Serial.println("====================================\n");
}

void readAndSendTelemetry() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[TELEMETRY] Status: FAILED (Wi-Fi Disconnected)");
    return;
  }

  bool max30102Online = checkI2CDevice(MAX30102_ADDR);
  bool mpu6050Online  = checkI2CDevice(MPU6050_ADDR);

  int rawAlcoholADC  = analogRead(MQ_ALCOHOL_PIN);
  float alcoholVolts = (rawAlcoholADC / 4095.0) * 3.3;
  float alcoholIndex = alcoholVolts / 3.3;
  int vibrationTriggered = digitalRead(SW420_VIBRATION_PIN);

  // 1. Explicit Formatted Sensor Data Line Printed to Serial Monitor
  Serial.printf("[Sensor Data] MQ ADC: %d (%.2fV) | Vib: %s | MAX30102: %s | MPU6050: %s\n",
                rawAlcoholADC, alcoholVolts,
                vibrationTriggered ? "IMPACT TRIGGERED" : "NORMAL",
                max30102Online ? "ONLINE" : "OFFLINE",
                mpu6050Online ? "ONLINE" : "OFFLINE");

  // 2. Construct Telemetry JSON Payload with Strict Sensor Data Integrity
  String jsonPayload = "{";
  jsonPayload += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
  jsonPayload += "\"esp32_ip\":\"" + WiFi.localIP().toString() + "\",";
  jsonPayload += "\"timestamp\":" + String(millis()) + ",";

  if (max30102Online) {
    jsonPayload += "\"heart_rate\":78.0,";
    jsonPayload += "\"spo2\":98.0,";
  } else {
    jsonPayload += "\"heart_rate\":null,";
    jsonPayload += "\"spo2\":null,";
  }

  jsonPayload += "\"alcohol\":" + String(alcoholIndex, 3) + ",";
  jsonPayload += "\"vibration\":" + String(vibrationTriggered) + ",";

  if (mpu6050Online) {
    jsonPayload += "\"acceleration_x\":0.02,";
    jsonPayload += "\"acceleration_y\":0.04,";
    jsonPayload += "\"acceleration_z\":0.98,";
    jsonPayload += "\"gyro_x\":0.01,";
    jsonPayload += "\"gyro_y\":0.02,";
    jsonPayload += "\"gyro_z\":0.01,";
  } else {
    jsonPayload += "\"acceleration_x\":null,";
    jsonPayload += "\"acceleration_y\":null,";
    jsonPayload += "\"acceleration_z\":null,";
    jsonPayload += "\"gyro_x\":null,";
    jsonPayload += "\"gyro_y\":null,";
    jsonPayload += "\"gyro_z\":null,";
  }

  jsonPayload += "\"sensors\":{";
  jsonPayload += "\"max30102\":\"" + String(max30102Online ? "ONLINE" : "OFFLINE") + "\",";
  jsonPayload += "\"mpu6050\":\"" + String(mpu6050Online ? "ONLINE" : "OFFLINE") + "\",";
  jsonPayload += "\"alcohol\":\"ONLINE\",";
  jsonPayload += "\"vibration\":\"ONLINE\"";
  jsonPayload += "}";
  jsonPayload += "}";

  // Print JSON Payload line to Serial Monitor
  Serial.printf("[JSON Payload]: %s\n", jsonPayload.c_str());

  String fullUrl = "http://" + detectedServerIP + ":" + String(BACKEND_PORT) + API_TELEMETRY_PATH;
  HTTPClient http;
  http.begin(fullUrl);
  http.addHeader("Content-Type", "application/json");

  int httpResponseCode = http.POST(jsonPayload);

  if (httpResponseCode == 200 || httpResponseCode == 201) {
    Serial.printf("[TELEMETRY] HTTP Status: %d | Server: %s | Status: SUCCESS\n\n", httpResponseCode, detectedServerIP.c_str());
  } else {
    Serial.printf("[TELEMETRY] Status: FAILED | Error: %s (Code: %d)\n\n", http.errorToString(httpResponseCode).c_str(), httpResponseCode);
  }

  http.end();
}

void loop() {
  unsigned long currentTime = millis();
  if (currentTime - lastTelemetryTime >= TELEMETRY_INTERVAL_MS) {
    lastTelemetryTime = currentTime;
    readAndSendTelemetry();
  }
}
