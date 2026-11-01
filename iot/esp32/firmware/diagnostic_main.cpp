/**
 * @file diagnostic_main.cpp
 * @brief SmartRoad AI — ESP32 Hardware Diagnostic Firmware
 * 
 * Performs:
 * 1. Serial Monitor init at 115200 baud.
 * 2. I2C Bus Scanner on SDA GPIO 21, SCL GPIO 22.
 * 3. MAX30102 sensor check (0x57).
 * 4. MPU6050 sensor check (0x68).
 * 5. MQ Alcohol ADC voltage reading on GPIO 34 (0–3.3V divider).
 * 6. SW-420 Vibration digital reading on GPIO 25.
 * 7. Wi-Fi Connection check (`AirFiber-aic9P`) with RSSI.
 */

#include <Arduino.h>
#include <WiFi.h>
#include <Wire.h>
#include "wifi_config.h"

#define I2C_SDA 21
#define I2C_SCL 22
#define SW420_VIBRATION_PIN 25
#define MQ_ALCOHOL_PIN 34

#define MAX30102_ADDR 0x57
#define MPU6050_ADDR 0x68

bool checkI2CDevice(uint8_t address) {
  Wire.beginTransmission(address);
  return (Wire.endTransmission() == 0);
}

void runI2CScanner() {
  Serial.println("\n==============================================");
  Serial.println("            ESP32 I2C BUS SCANNER             ");
  Serial.println("==============================================");
  
  bool max30102Found = checkI2CDevice(MAX30102_ADDR);
  bool mpu6050Found  = checkI2CDevice(MPU6050_ADDR);

  Serial.printf("MAX30102 (0x57): %s\n", max30102Found ? "FOUND" : "NOT FOUND / DISCONNECTED");
  Serial.printf("MPU6050  (0x68): %s\n", mpu6050Found  ? "FOUND" : "NOT FOUND / DISCONNECTED");
  Serial.println("----------------------------------------------");
}

void connectWiFi() {
  Serial.println("\n[WiFi] Initializing Wi-Fi Connection...");
  Serial.printf("[WiFi] SSID: %s\n", WIFI_SSID);
  
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 15) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WiFi] STATUS: CONNECTED");
    Serial.printf("[WiFi] ESP32 IP: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("[WiFi] RSSI Signal: %d dBm\n", WiFi.RSSI());
  } else {
    Serial.println("\n[WiFi] STATUS: DISCONNECTED (Local sensor diagnostics continuing...)");
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n==============================================");
  Serial.println("   SMARTROAD AI — HARDWARE DIAGNOSTIC FIRMWARE ");
  Serial.println("==============================================");

  pinMode(SW420_VIBRATION_PIN, INPUT);
  pinMode(MQ_ALCOHOL_PIN, INPUT);

  Wire.begin(I2C_SDA, I2C_SCL);
  Serial.printf("[I2C] Bus Initialized on SDA: GPIO %d, SCL: GPIO %d\n", I2C_SDA, I2C_SCL);

  runI2CScanner();
  connectWiFi();
}

void loop() {
  Serial.println("\n--- HARDWARE DIAGNOSTIC SAMPLE ---");

  // 1. I2C Sensors Status
  bool max30102Online = checkI2CDevice(MAX30102_ADDR);
  bool mpu6050Online  = checkI2CDevice(MPU6050_ADDR);

  Serial.printf("MAX30102 STATUS: %s\n", max30102Online ? "CONNECTED" : "DISCONNECTED");
  Serial.printf("MPU6050  STATUS: %s\n", mpu6050Online  ? "CONNECTED" : "DISCONNECTED");

  // 2. Analog MQ Alcohol Sensor (GPIO 34)
  int rawADC = analogRead(MQ_ALCOHOL_PIN);
  float voltage = (rawADC / 4095.0) * 3.3;
  Serial.printf("MQ RAW ADC (GPIO 34): %d | Voltage: %.2f V | ALCOHOL SENSOR INDEX: %.3f\n", rawADC, voltage, voltage / 3.3);

  // 3. Digital SW-420 Vibration Sensor (GPIO 25)
  int vibrationState = digitalRead(SW420_VIBRATION_PIN);
  Serial.printf("VIBRATION SENSOR (GPIO 25): %s\n", vibrationState == HIGH ? "VIBRATION DETECTED / IMPACT" : "NORMAL");

  // 4. Wi-Fi Status
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("WIFI STATUS: CONNECTED | IP: %s | RSSI: %d dBm\n", WiFi.localIP().toString().c_str(), WiFi.RSSI());
  } else {
    Serial.println("WIFI STATUS: DISCONNECTED");
  }

  delay(2000);
}
