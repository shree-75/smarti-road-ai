import asyncio
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import jwt

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.models.telemetry import Telemetry
from app.schemas.telemetry import TelemetryCreate, TelemetryResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/telemetry", tags=["telemetry"])

class ConnectionManager:
    """
    Manages active WebSocket connections indexed by user ID to guarantee user isolation,
    with global broadcast capability for IoT & camera telemetry streams.
    """
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            dead_sockets = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    dead_sockets.append(connection)
            for dead_socket in dead_sockets:
                self.disconnect(dead_socket, user_id)

    async def broadcast(self, message: dict):
        """
        Broadcasts message to all active WebSocket clients.
        """
        for user_id, connections in list(self.active_connections.items()):
            dead_sockets = []
            for connection in list(connections):
                try:
                    await connection.send_json(message)
                except Exception:
                    dead_sockets.append(connection)
            for dead_socket in dead_sockets:
                self.disconnect(dead_socket, user_id)

manager = ConnectionManager()

def broadcast_telemetry_update(message: dict):
    """
    Module-level helper to broadcast real-time telemetry or IoT updates
    across active WebSocket connections.
    """
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            loop.create_task(manager.broadcast(message))
    except RuntimeError:
        pass

def parse_ws_token(token: str) -> int:
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if not user_id or token_type != "access":
            raise ValueError("Invalid token type or subject")
        return int(user_id)
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@router.websocket("/ws")
async def websocket_telemetry(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    Authenticated WebSocket endpoint streaming live telemetry to the connected user.
    """
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        user_id = parse_ws_token(token)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception:
        manager.disconnect(websocket, user_id)

@router.post("", response_model=TelemetryResponse, status_code=status.HTTP_201_CREATED)
async def create_telemetry(
    telemetry_in: TelemetryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Records a new telemetry entry in SQLite and broadcasts it over WebSocket.
    """
    telemetry_data = telemetry_in.model_dump()
    timestamp = telemetry_data.pop("timestamp", None) or datetime.now(timezone.utc)

    telemetry = Telemetry(
        user_id=current_user.id,
        timestamp=timestamp,
        **telemetry_data
    )
    db.add(telemetry)
    db.commit()
    db.refresh(telemetry)

    # Broadcast to authenticated user's WebSockets only after successful DB commit
    serialized_payload = jsonable_encoder(TelemetryResponse.model_validate(telemetry))
    await manager.send_personal_message(
        message={
            "type": "telemetry",
            "data": serialized_payload
        },
        user_id=current_user.id
    )

    return telemetry

@router.get("", response_model=List[TelemetryResponse])
def get_telemetry_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves telemetry log history for the authenticated user (newest first).
    """
    records = (
        db.query(Telemetry)
        .filter(Telemetry.user_id == current_user.id)
        .order_by(Telemetry.timestamp.desc())
        .limit(limit)
        .all()
    )
    return records

@router.get("/latest", response_model=TelemetryResponse)
def get_latest_telemetry(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the single most recent telemetry record for the authenticated user.
    """
    record = (
        db.query(Telemetry)
        .filter(Telemetry.user_id == current_user.id)
        .order_by(Telemetry.timestamp.desc())
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No telemetry records found for current user."
        )
    return record
