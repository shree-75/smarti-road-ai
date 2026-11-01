import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.user import User
from app.models.session import DriverSession
from app.schemas.session import DriverSessionCreate, DriverSessionEnd, DriverSessionResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/sessions", tags=["driver-sessions"])

@router.post("/start", response_model=DriverSessionResponse, status_code=status.HTTP_201_CREATED)
def start_driver_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Starts a new active driving/monitoring session for the authenticated user.
    Auto-completes any previous orphaned active sessions for safety.
    """
    # Auto-complete any existing active sessions
    active_sessions = (
        db.query(DriverSession)
        .filter(DriverSession.user_id == current_user.id, DriverSession.status == "active")
        .all()
    )
    now = datetime.now(timezone.utc)
    for s in active_sessions:
        s.status = "completed"
        s.end_time = now
        if s.start_time:
            # Handle naive or tz-aware subtraction safely
            start_t = s.start_time if s.start_time.tzinfo else s.start_time.replace(tzinfo=timezone.utc)
            s.duration_sec = max(0.0, (now - start_t).total_seconds())

    session_code = f"SESS-{uuid.uuid4().hex[:8].upper()}"
    new_session = DriverSession(
        user_id=current_user.id,
        session_code=session_code,
        start_time=now,
        status="active"
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.post("/end", response_model=DriverSessionResponse)
def end_driver_session(
    session_end_in: DriverSessionEnd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Closes the current active driving session for the authenticated user and records aggregate statistics.
    """
    active_session = (
        db.query(DriverSession)
        .filter(DriverSession.user_id == current_user.id, DriverSession.status == "active")
        .order_by(DriverSession.start_time.desc())
        .first()
    )
    if not active_session:
        # If no active session, retrieve the latest completed session or raise HTTP 404
        latest_session = (
            db.query(DriverSession)
            .filter(DriverSession.user_id == current_user.id)
            .order_by(DriverSession.start_time.desc())
            .first()
        )
        if not latest_session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active driver session found to terminate.")
        return latest_session

    now = datetime.now(timezone.utc)
    start_t = active_session.start_time if active_session.start_time.tzinfo else active_session.start_time.replace(tzinfo=timezone.utc)
    
    active_session.end_time = now
    active_session.duration_sec = max(0.0, (now - start_t).total_seconds())
    active_session.status = "completed"
    
    end_data = session_end_in.model_dump(exclude_unset=True)
    for key, val in end_data.items():
        setattr(active_session, key, val)

    db.commit()
    db.refresh(active_session)
    return active_session

@router.get("", response_model=List[DriverSessionResponse])
def get_driver_sessions(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves driving session history for the authenticated user.
    """
    sessions = (
        db.query(DriverSession)
        .filter(DriverSession.user_id == current_user.id)
        .order_by(DriverSession.start_time.desc())
        .limit(limit)
        .all()
    )
    return sessions

@router.get("/latest", response_model=DriverSessionResponse)
def get_latest_driver_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the current active or most recent driver session for the authenticated user.
    """
    session = (
        db.query(DriverSession)
        .filter(DriverSession.user_id == current_user.id)
        .order_by(DriverSession.start_time.desc())
        .first()
    )
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No driver session records found.")
    return session
