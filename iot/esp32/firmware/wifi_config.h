/**
 * @file wifi_config.h
 * @brief SmartRoad AI - ESP32 Wi-Fi & PC LAN Configuration Header
 * 
 * Active Network Configuration:
 * SSID: sb (2.4 GHz Wi-Fi 4)
 * PC LAN IP: 10.105.159.142
 */

#ifndef WIFI_CONFIG_H
#define WIFI_CONFIG_H

// Active Wi-Fi Credentials
const char* WIFI_SSID = "sb";
const char* WIFI_PASS = "mrdu@1234";

// Active Laptop IPv4 Address & Ports
const char* SERVER_IP   = "10.105.159.142";
const int   SERVER_PORT = 8000;
const char* API_PATH    = "/api/v1/iot/telemetry";

#endif // WIFI_CONFIG_H
