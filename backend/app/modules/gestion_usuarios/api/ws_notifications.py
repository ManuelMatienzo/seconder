from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from app.core.database import SessionLocal
from app.models import User
from app.shared.realtime import notification_manager
from app.shared.security.security import decode_access_token

router = APIRouter()


@router.websocket("/ws/notifications")
async def notifications_ws(websocket: WebSocket) -> None:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub", ""))
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if not user or user.status != "activo":
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await notification_manager.connect(websocket, user_id)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            pass
        finally:
            notification_manager.disconnect(websocket, user_id)
    finally:
        db.close()
