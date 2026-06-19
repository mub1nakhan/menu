"""
WebSocket handler for Kitchen Display System (KDS)
"""

from fastapi import WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import json
import logging
from typing import Set, Dict

from app.core.database import get_db
from app.core.security import verify_token
from app.models import Order, User

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[UUID, Set[WebSocket]] = {}
        self.kitchen_connections: Dict[UUID, WebSocket] = {}  # kitchen_id -> ws
    
    async def connect(self, websocket: WebSocket, branch_id: UUID):
        """Add new connection"""
        await websocket.accept()
        if branch_id not in self.active_connections:
            self.active_connections[branch_id] = set()
        self.active_connections[branch_id].add(websocket)
        logger.info(f"Client connected to branch {branch_id}")
    
    async def disconnect(self, websocket: WebSocket, branch_id: UUID):
        """Remove connection"""
        if branch_id in self.active_connections:
            self.active_connections[branch_id].discard(websocket)
    
    async def broadcast_to_branch(self, branch_id: UUID, message: dict):
        """Send message to all clients in a branch"""
        if branch_id not in self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections[branch_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.add(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            await self.disconnect(conn, branch_id)
    
    async def send_order_update(self, branch_id: UUID, order: Order):
        """Send order update to kitchen"""
        message = {
            "type": "order_update",
            "order_id": str(order.id),
            "status": order.status,
            "items": [
                {
                    "id": str(item.id),
                    "product": item.product.name_i18n.get("en", "Unknown"),
                    "quantity": item.quantity,
                    "status": item.status,
                    "notes": item.notes,
                }
                for item in order.items
            ],
            "timestamp": order.updated_at.isoformat(),
        }
        
        await self.broadcast_to_branch(branch_id, message)


manager = ConnectionManager()


async def get_token_from_query(token: str = Query(...)) -> dict:
    """Extract token from query parameter"""
    payload = verify_token(token)
    if not payload:
        raise ValueError("Invalid token")
    return payload


async def websocket_endpoint(
    websocket: WebSocket,
    branch_id: UUID,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """WebSocket endpoint for kitchen display system"""
    
    # Verify token
    payload = verify_token(token)
    if not payload:
        await websocket.close(code=1008, reason="Unauthorized")
        return
    
    user_id = UUID(payload.get("user_id"))
    
    # Get user and verify branch access
    user = await db.get(User, user_id)
    if not user or (user.branch_id and user.branch_id != branch_id):
        await websocket.close(code=1008, reason="No access to branch")
        return
    
    await manager.connect(websocket, branch_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                # Heartbeat
                await websocket.send_json({"type": "pong"})
            
            elif message.get("type") == "status_update":
                # Update order status (only for chefs)
                if user.role.code not in ["chef", "manager", "owner"]:
                    continue
                
                order_id = UUID(message.get("order_id"))
                order = await db.get(Order, order_id)
                
                if order and order.branch_id == branch_id:
                    order.status = message.get("status")
                    
                    # Update item status if provided
                    for item_data in message.get("items", []):
                        item_id = UUID(item_data["id"])
                        item = next((i for i in order.items if i.id == item_id), None)
                        if item:
                            item.status = item_data.get("status")
                    
                    await db.commit()
                    await manager.send_order_update(branch_id, order)
    
    except WebSocketDisconnect:
        await manager.disconnect(websocket, branch_id)
        logger.info(f"Client disconnected from branch {branch_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket, branch_id)

