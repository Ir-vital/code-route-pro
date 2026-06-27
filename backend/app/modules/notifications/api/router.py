"""
Router FastAPI du module notifications.
REST : /api/v1/notifications
WebSocket : /ws/notifications
"""

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.api.dependencies import CurrentUser
from app.modules.notifications.infrastructure.models import NotificationModel
from app.modules.notifications.infrastructure.ws_manager import ws_manager
from app.shared.domain.enums import NotificationType
from app.shared.pagination import PaginatedResponse, PaginationParams

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class NotificationResponse(BaseModel):
    id: uuid.UUID
    type: NotificationType
    title: str
    message: str
    payload: dict | None = None
    is_read: bool
    created_at: datetime


@router.get("/", response_model=PaginatedResponse[NotificationResponse])
async def list_notifications(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PaginatedResponse[NotificationResponse]:
    params = PaginationParams(page=page, page_size=page_size)

    cq = select(func.count()).select_from(NotificationModel).where(
        NotificationModel.user_id == current_user.id
    )
    total = (await db.execute(cq)).scalar_one()

    result = await db.execute(
        select(NotificationModel)
        .where(NotificationModel.user_id == current_user.id)
        .order_by(NotificationModel.created_at.desc())
        .offset(params.offset)
        .limit(params.limit)
    )
    items = [
        NotificationResponse(
            id=n.id, type=n.type, title=n.title, message=n.message,
            payload=n.payload, is_read=n.is_read, created_at=n.created_at,
        )
        for n in result.scalars().all()
    ]
    return PaginatedResponse.create(items=items, total=total, params=params)


@router.patch("/{notification_id}/read", response_model=dict)
async def mark_as_read(
    notification_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    await db.execute(
        update(NotificationModel)
        .where(
            NotificationModel.id == notification_id,
            NotificationModel.user_id == current_user.id,
        )
        .values(is_read=True)
    )
    return {"message": "Notification marquée comme lue"}


@router.patch("/read-all", response_model=dict)
async def mark_all_read(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    await db.execute(
        update(NotificationModel)
        .where(
            NotificationModel.user_id == current_user.id,
            NotificationModel.is_read == False,  # noqa: E712
        )
        .values(is_read=True)
    )
    return {"message": "Toutes les notifications marquées comme lues"}


# ─── WebSocket ────────────────────────────────────────────────────────────────
ws_router = APIRouter(tags=["Notifications — WebSocket"])


@ws_router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str | None = Query(default=None),
) -> None:
    """
    Connexion WebSocket pour les notifications temps réel.
    Le token JWT est passé en query param : /ws/notifications?token=<access_token>
    Scalable horizontalement via Redis pub/sub.
    """
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    from app.core.security import verify_access_token
    from jose import JWTError
    try:
        payload = verify_access_token(token)
        user_id = payload["sub"]
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await ws_manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id, websocket)
