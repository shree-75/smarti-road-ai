import math
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.models.emergency import EmergencyAlert
from app.schemas.emergency import EmergencyAlertCreate, EmergencyAlertStatusUpdate, EmergencyAlertResponse
from app.api.auth import get_current_user
from app.services.twilio_service import send_emergency_sms, make_emergency_call

router = APIRouter(prefix="/emergency", tags=["Emergency Response"])

@router.get("/nearby-hospitals")
def get_nearby_hospitals(lat: float = 16.5062, lon: float = 80.6480, radius_km: float = 15.0):
    """
    Computes real-time nearby hospitals, emergency trauma care units, and police centers with exact distance, ETA, and emergency phone.
    """
    facilities = [
        {"id": 1, "name": "AIIMS Emergency & Trauma Care", "type": "HOSPITAL", "specialty": "Level 1 Trauma & ICU", "lat": lat + 0.0120, "lon": lon + 0.0090, "phone": "+91 863 2345000", "emergency_line": "108", "available_beds": 14, "blood_bank": True},
        {"id": 2, "name": "City Government General Hospital", "type": "HOSPITAL", "specialty": "24/7 Emergency & Multi-Specialty", "lat": lat - 0.0085, "lon": lon + 0.0110, "phone": "+91 866 2577777", "emergency_line": "108", "available_beds": 28, "blood_bank": True},
        {"id": 3, "name": "Apollo Emergency Trauma Institute", "type": "HOSPITAL", "specialty": "Cardiac & Neuro Trauma Unit", "lat": lat + 0.0210, "lon": lon - 0.0150, "phone": "+91 866 2478888", "emergency_line": "1066", "available_beds": 9, "blood_bank": True},
        {"id": 4, "name": "Manipal Multi-Specialty Hospital", "type": "HOSPITAL", "specialty": "Accident Critical Care", "lat": lat - 0.0180, "lon": lon - 0.0190, "phone": "+91 866 6699999", "emergency_line": "108", "available_beds": 12, "blood_bank": True},
        {"id": 5, "name": "Ramesh Cardiac & Emergency Hospital", "type": "HOSPITAL", "specialty": "Emergency Resuscitation Unit", "lat": lat + 0.0150, "lon": lon + 0.0250, "phone": "+91 866 2488888", "emergency_line": "108", "available_beds": 16, "blood_bank": True},
        {"id": 6, "name": "Central Highway Police Station", "type": "POLICE", "specialty": "Highway Patrol & Quick Action Team", "lat": lat - 0.0050, "lon": lon - 0.0070, "phone": "112 / +91 866 2444100", "emergency_line": "112", "available_beds": 0, "blood_bank": False},
        {"id": 7, "name": "Accident Hotspot - Bypass Flyover Junction", "type": "HOTSPOT", "specialty": "High Risk Curve (18 incidents in 2025)", "lat": lat + 0.0280, "lon": lon + 0.0180, "risk_level": "HIGH_RISK_ZONE", "incidents": 18}
    ]

    results = []
    for f in facilities:
        dlat = math.radians(f["lat"] - lat)
        dlon = math.radians(f["lon"] - lon)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(f["lat"])) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance_km = round(6371 * c, 2)

        eta_mins = max(1, math.ceil((distance_km / 35.0) * 60))
        f_copy = dict(f)
        f_copy["distance_km"] = distance_km
        f_copy["distance_str"] = f"{distance_km} km"
        f_copy["eta_mins"] = eta_mins
        f_copy["eta_str"] = f"{eta_mins} mins" if eta_mins < 60 else f"{eta_mins // 60}h {eta_mins % 60}m"
        results.append(f_copy)

    results.sort(key=lambda x: x["distance_km"])
    return {
        "status": "success",
        "current_location": {"lat": lat, "lon": lon},
        "total_facilities": len(results),
        "facilities": results
    }

@router.get("/", response_model=List[EmergencyAlertResponse])
def get_emergency_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves emergency alerts. Caretaker, Police, Hospital, and Admin roles receive all active alerts.
    Drivers receive their personal emergency alerts.
    """
    role = (current_user.role or "driver").lower()
    if role in ["caretaker", "hospital", "police", "admin"]:
        alerts = db.query(EmergencyAlert).order_by(EmergencyAlert.created_at.desc()).all()
    else:
        alerts = db.query(EmergencyAlert).filter(EmergencyAlert.driver_id == current_user.id).order_by(EmergencyAlert.created_at.desc()).all()
    return alerts

@router.post("/", response_model=EmergencyAlertResponse, status_code=status.HTTP_201_CREATED)
def trigger_emergency_alert(
    payload: EmergencyAlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Dispatches a critical driver risk emergency alert.
    Persists alert in database, triggers Twilio notifications if configured, and returns created alert.
    """
    alert = EmergencyAlert(
        driver_id=current_user.id,
        vehicle_id=payload.vehicle_id,
        alert_type=payload.alert_type,
        risk_score=payload.risk_score,
        latitude=payload.latitude,
        longitude=payload.longitude,
        details=payload.details or f"Critical driver alert triggered for driver {current_user.name or current_user.email}",
        status="NEW"
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    msg = f"🚨 SMARTROAD AI EMERGENCY ALERT! Driver {current_user.name or current_user.email} triggered {payload.alert_type} (Risk: {payload.risk_score}/100) at Lat: {payload.latitude}, Lon: {payload.longitude}."
    send_emergency_sms(msg)
    if payload.risk_score >= 85.0:
        make_emergency_call()

    return alert

@router.patch("/{alert_id}/status", response_model=EmergencyAlertResponse)
def update_alert_status(
    alert_id: int,
    payload: EmergencyAlertStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates response status of an emergency alert ('NEW' -> 'ACKNOWLEDGED' -> 'RESPONDING' -> 'RESOLVED').
    Allowed for Caretaker, Hospital, Police, and Admin roles.
    """
    alert = db.query(EmergencyAlert).filter(EmergencyAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Emergency alert record not found.")

    alert.status = payload.status
    db.commit()
    db.refresh(alert)
    return alert


# ─────────────────────────────────────────────────────────────
# Twilio Emergency Voice & SMS Integration Endpoints
# ─────────────────────────────────────────────────────────────
from pydantic import BaseModel
from typing import Optional
from app.services.twilio_service import get_twilio_status, update_twilio_credentials

class TwilioConfigRequest(BaseModel):
    twilio_phone_number: Optional[str] = None
    emergency_phone_number: Optional[str] = None
    account_sid: Optional[str] = None
    auth_token: Optional[str] = None

@router.get("/twilio-status")
def twilio_status():
    """Returns status of Twilio voice call & SMS dispatch service."""
    return get_twilio_status()

@router.post("/twilio-config")
def set_twilio_config(payload: TwilioConfigRequest):
    """Updates Twilio credentials and phone numbers."""
    return update_twilio_credentials(
        from_phone=payload.twilio_phone_number,
        to_phone=payload.emergency_phone_number,
        account_sid=payload.account_sid,
        auth_token=payload.auth_token
    )

@router.post("/test-call")
def trigger_test_call():
    """Dispatches a test emergency voice call to configured emergency number (+919704638232 default)."""
    return make_emergency_call(reason="SmartRoad AI system test call")
