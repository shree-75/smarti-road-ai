import socket
import threading
import json
import time

def get_lan_ip() -> str:
    """
    Dynamically determines the machine's primary usable LAN/Wi-Fi IPv4 address.
    Connects to an external IP via UDP to inspect the OS routing table without sending packets.
    Never hardcodes an IP or returns 127.0.0.1 if an active network interface exists.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Trigger OS routing table lookup for primary active interface
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
        except Exception:
            ip = "127.0.0.1"
    finally:
        s.close()

    if ip.startswith("127.") or ip == "0.0.0.0":
        try:
            s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s2.connect(("192.168.1.1", 80))
            ip = s2.getsockname()[0]
            s2.close()
        except Exception:
            pass

    return ip


def start_udp_discovery_server(port: int = 8001):
    """
    Starts a background UDP server on port 8001 that listens for broadcast queries from ESP32.
    When ESP32 broadcasts 'SMARTROAD_SERVER_DISCOVERY', this server responds with current LAN IP and port.
    """
    def _listen():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("0.0.0.0", port))
        except Exception as e:
            print(f"[UDP Discovery] Could not bind to port {port}: {e}")
            return

        print(f"[UDP Discovery] Listening for ESP32 broadcast queries on UDP port {port}...")

        while True:
            try:
                data, addr = sock.recvfrom(1024)
                message = data.decode("utf-8", errors="ignore").strip()
                if "SMARTROAD" in message or "DISCOVER" in message:
                    current_ip = get_lan_ip()
                    response = json.dumps({
                        "server_ip": current_ip,
                        "server_port": 8000,
                        "telemetry_url": f"http://{current_ip}:8000/api/v1/iot/telemetry",
                        "config_url": f"http://{current_ip}:8000/api/v1/iot/config"
                    })
                    sock.sendto(response.encode("utf-8"), addr)
                    print(f"[UDP Discovery] Responded to ESP32 at {addr[0]} -> Server IP: {current_ip}")
            except Exception as e:
                time.sleep(1)

    t = threading.Thread(target=_listen, daemon=True)
    t.start()
