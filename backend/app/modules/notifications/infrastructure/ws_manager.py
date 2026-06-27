"""
Gestionnaire WebSocket scalable via Redis pub/sub.

Architecture :
  - Chaque instance du serveur maintient ses connexions WebSocket en mémoire.
  - Pour envoyer à un user, on publie dans Redis sur le channel "ws:user:<user_id>".
  - Chaque instance souscrit à tous les channels et dispatche aux WS locaux.
  - Résultat : fonctionne avec N instances (load balancer, K8s, etc.).

Channel Redis : "ws:notifications:<user_id>"
"""

import asyncio
import json
import logging
from collections import defaultdict

from fastapi import WebSocket

logger = logging.getLogger(__name__)

CHANNEL_PREFIX = "ws:notifications:"


class RedisWebSocketManager:
    """
    Gestionnaire WebSocket avec Redis pub/sub pour la scalabilité horizontale.
    """

    def __init__(self) -> None:
        # Connexions locales : user_id → set de WebSockets
        self._local_connections: dict[str, set[WebSocket]] = defaultdict(set)
        self._pubsub_task: asyncio.Task | None = None

    async def start(self) -> None:
        """Lance la tâche de souscription Redis en arrière-plan."""
        if self._pubsub_task and not self._pubsub_task.done():
            return
        self._pubsub_task = asyncio.create_task(self._redis_listener())
        logger.info("WebSocket Redis pub/sub listener started")

    async def stop(self) -> None:
        """Arrête proprement la tâche Redis."""
        if self._pubsub_task:
            self._pubsub_task.cancel()
            try:
                await self._pubsub_task
            except asyncio.CancelledError:
                pass

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._local_connections[user_id].add(websocket)
        logger.debug("WS connected", extra={"user_id": user_id})

    def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        self._local_connections[user_id].discard(websocket)
        if not self._local_connections[user_id]:
            del self._local_connections[user_id]
        logger.debug("WS disconnected", extra={"user_id": user_id})

    async def send_to_user(self, user_id: str, message: dict) -> None:
        """
        Publie le message dans Redis → toutes les instances le reçoivent
        et le dispatche aux WebSockets locaux de cet utilisateur.
        """
        try:
            from app.core.redis import get_redis_pool
            redis = await get_redis_pool()
            channel = f"{CHANNEL_PREFIX}{user_id}"
            await redis.publish(channel, json.dumps(message))
        except Exception as e:
            logger.warning("Redis publish failed, falling back to local dispatch", extra={"error": str(e)})
            # Fallback : dispatch local uniquement
            await self._dispatch_local(user_id, message)

    async def _dispatch_local(self, user_id: str, message: dict) -> None:
        """Envoie directement aux WebSockets locaux de cet utilisateur."""
        dead: set[WebSocket] = set()
        for ws in list(self._local_connections.get(user_id, set())):
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self._local_connections[user_id].discard(ws)

    async def _redis_listener(self) -> None:
        """
        Souscrit au pattern Redis et dispatche les messages reçus
        aux WebSockets locaux.
        """
        while True:
            try:
                from app.core.redis import get_redis_pool
                redis = await get_redis_pool()
                pubsub = redis.pubsub()
                await pubsub.psubscribe(f"{CHANNEL_PREFIX}*")
                logger.info("Subscribed to Redis pattern", extra={"pattern": f"{CHANNEL_PREFIX}*"})

                async for raw_message in pubsub.listen():
                    if raw_message["type"] != "pmessage":
                        continue
                    try:
                        channel: str = raw_message["channel"]
                        user_id = channel.removeprefix(CHANNEL_PREFIX)
                        data = json.loads(raw_message["data"])
                        await self._dispatch_local(user_id, data)
                    except Exception as e:
                        logger.warning("WS dispatch error", extra={"error": str(e)})

            except asyncio.CancelledError:
                logger.info("Redis WS listener cancelled")
                return
            except Exception as e:
                logger.error("Redis listener error, retrying in 3s", extra={"error": str(e)})
                await asyncio.sleep(3)


# ─── Instance globale ─────────────────────────────────────────────────────────
ws_manager = RedisWebSocketManager()
