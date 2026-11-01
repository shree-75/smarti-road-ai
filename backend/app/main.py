from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys

try:
    if sys.stdout:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if sys.stderr:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

from app.core.config import settings
from app.core.network import get_lan_ip, start_udp_discovery_server
from app.api.auth import router as auth_router
from app.api.telemetry import router as telemetry_router
from app.api.session import router as session_router
from app.api.profile import router as profile_router
from app.api.vehicle import router as vehicle_router
from app.api.emergency import router as emergency_router
from app.api.iot import router as iot_router
from app.api.vision import router as vision_router

from app.db.session import engine, Base
import app.models.user
import app.models.telemetry
import app.models.session
import app.models.profile
import app.models.vehicle
import app.models.emergency
import app.models.iot

# Create tables automatically for local/SQLite dev
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print("Database metadata creation skipped or failed:", e)

def print_startup_network_banner():
    lan_ip = get_lan_ip()
    port = 8000
    print("\n====================================================")
    print("SMARTROAD AI NETWORK CONFIGURATION")
    print("====================================================")
    print(f"Server LAN IP : {lan_ip}")
    print(f"Backend Port  : {port}")
    print(f"API URL       : http://{lan_ip}:{port}")
    print(f"Telemetry URL : http://{lan_ip}:{port}/api/v1/iot/telemetry")
    print(f"Frontend      : http://localhost:5173")
    print("====================================================")

    # Firewall & Host binding check
    if lan_ip.startswith("127."):
        print("[WARNING] BACKEND IS LOCALHOST ONLY — External LAN devices like ESP32 cannot reach the backend.")
        print("   Connect to a Wi-Fi or Mobile Hotspot network so ESP32 can connect.")
    else:
        print(f"[OK] Active LAN IP detected: {lan_ip}")
        print("   To allow external TCP connections on Windows Firewall if blocked, run:")
        print('   netsh advfirewall firewall add rule name="SmartRoad AI Port 8000" dir=in action=allow protocol=TCP localport=8000')
    print("====================================================\n")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    print_startup_network_banner()
    start_udp_discovery_server(port=8001)
    try:
        from app.api.vision import _engine
        _engine.start()
        print("[Startup] Real-time AI Vision & Driver Camera Stream initiated.")
    except Exception as e:
        print("[Startup] Vision stream startup error:", e)
    yield
    # Shutdown actions
    try:
        from app.api.vision import _engine
        _engine.stop()
    except Exception:
        pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=r"https://.*\.netlify\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(telemetry_router, prefix=settings.API_V1_STR)
app.include_router(session_router, prefix=settings.API_V1_STR)
app.include_router(profile_router, prefix=settings.API_V1_STR)
app.include_router(vehicle_router, prefix=settings.API_V1_STR)
app.include_router(emergency_router, prefix=settings.API_V1_STR)
app.include_router(iot_router, prefix=settings.API_V1_STR)
app.include_router(vision_router, prefix=settings.API_V1_STR)


@app.get("/")
def read_root():
    lan_ip = get_lan_ip()
    return {
        "message": "Welcome to SmartRoad AI Telemetry & Emergency Response Service",
        "server_ip": lan_ip,
        "telemetry_url": f"http://{lan_ip}:8000/api/v1/iot/telemetry"
    }
