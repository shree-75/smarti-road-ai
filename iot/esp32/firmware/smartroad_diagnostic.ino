/**
 * @file smartroad_diagnostic.ino
 * @brief Arduino IDE standalone Hardware Diagnostic sketch for SmartRoad AI
 */

#include <WiFi.h>
#include <Wire.h>

// Wi-Fi Access Point Credentials
const char* WIFI_SSID = "AirFiber-aic9P";
const char* WIFI_PASS = "vijaya07";

#define I2C_SDA 21
#define I2C_SCL 22
#define SW420_VIBRATION_PIN 25
#define MQ_ALCOHOL_PIN 34

#define MAX30102_ADDR 0x57
#define MPU6050_ADDR 0x68

bool checkI2C(uint8_t addr) {
  Wire.beginTransmission(addr);
  return (Wire.endTransmission() == 0);
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n=== SMARTROAD AI HARDWARE DIAGNOSTICS ===");
  pinMode(SW420_VIBRATION_PIN, INPUT);
  pinMode(MQ_ALCOHOL_PIN, INPUT);

  Wire.begin(I2C_SDA, I2C_SCL);

  Serial.println("I2C SCAN:");
  Serial.printf("MAX30102 (0x57): %s\n", checkI2C(MAX30102_ADDR) ? "FOUND" : "NOT FOUND");
  Serial.printf("MPU6050  (0x68): %s\n", checkI2C(MPU6050_ADDR)  ? "FOUND" : "NOT FOUND");

  WiFi.begin(WIFI_SSID, WIFI_PASS);
}

void loop() {
  Serial.println("\n--- SENSOR READINGS ---");
  bool max30102Ok = checkI2C(MAX30102_ADDR);
  bool mpu6050Ok  = checkI2C(MPU6050_ADDR);

  Serial.printf("MAX30102 STATUS: %s\n", max30102Ok ? "CONNECTED" : "DISCONNECTED");
  Serial.printf("MPU6050  STATUS: %s\n", mpu6050Ok  ? "CONNECTED" : "DISCONNECTED");

  int rawADC = analogRead(MQ_ALCOHOL_PIN);
  float volts = (rawADC / 4095.0) * 3.3;
  Serial.printf("MQ RAW ADC (GPIO 34): %d | Volts: %.2fV | ALCOHOL SENSOR INDEX: %.3f\n", rawADC, volts, volts / 3.3);

  int vib = digitalRead(SW420_VIBRATION_PIN);
  Serial.printf("VIBRATION SENSOR (GPIO 25): %s\n", vib == HIGH ? "VIBRATION DETECTED" : "NORMAL");

  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("WiFi: CONNECTED | IP: %s | RSSI: %d dBm\n", WiFi.localIP().toString().c_str(), WiFi.RSSI());
  } else {
    Serial.println("WiFi: DISCONNECTED");
  }

  delay(2000);
}
