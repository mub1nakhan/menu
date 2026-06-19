"""
Orders API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID
from typing import List, Optional

from app.core.database import get_db
from app.models import Order, OrderItem, OrderStatusHistory, User, Table
from app.schemas.auth import UserResponse
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("", response_model=List[dict])
async def list_orders(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
):
    """List orders for current user's restaurant"""
    query = select(Order).where(
        Order.restaurant_id == current_user.restaurant_id
    )
    
    if status:
        query = query.where(Order.status == status)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    return [
        {
            "id": str(order.id),
            "table_id": str(order.table_id) if order.table_id else None,
            "status": order.status,
            "total_amount": float(order.total_amount),
            "created_at": order.created_at.isoformat(),
            "items_count": len(order.items),
        }
        for order in orders
    ]


@router.post("")
async def create_order(
    order_data: dict,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create new order"""
    try:
        # Create order
        order = Order(
            restaurant_id=current_user.restaurant_id,
            branch_id=current_user.branch_id or UUID('00000000-0000-0000-0000-000000000000'),  # Will need to be passed
            table_id=order_data.get("table_id"),
            order_type=order_data.get("order_type", "dine_in"),
            created_by_id=current_user.id,
        )
        
        db.add(order)
        await db.flush()
        
        # Add items
        for item_data in order_data.get("items", []):
            item = OrderItem(
                order_id=order.id,
                product_id=item_data["product_id"],
                quantity=item_data["quantity"],
                unit_price=item_data.get("unit_price", 0),
            )
            db.add(item)
            order.total_amount += float(item_data.get("unit_price", 0)) * item_data["quantity"]
        
        await db.commit()
        
        return {
            "id": str(order.id),
            "status": order.status,
            "total_amount": float(order.total_amount),
            "created_at": order.created_at.isoformat(),
        }
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{order_id}")
async def get_order(
    order_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get order details"""
    order = await db.get(Order, order_id)
    
    if not order or order.restaurant_id != current_user.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    
    return {
        "id": str(order.id),
        "status": order.status,
        "total_amount": float(order.total_amount),
        "items": [
            {
                "id": str(item.id),
                "product_id": str(item.product_id),
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "status": item.status,
            }
            for item in order.items
        ],
        "created_at": order.created_at.isoformat(),
    }


@router.put("/{order_id}/status")
async def update_order_status(
    order_id: UUID,
    status_data: dict,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update order status"""
    order = await db.get(Order, order_id)
    
    if not order or order.restaurant_id != current_user.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    
    old_status = order.status
    order.status = status_data.get("status", order.status)
    
    # Create status history
    history = OrderStatusHistory(
        order_id=order.id,
        from_status=old_status,
        to_status=order.status,
        changed_by_id=current_user.id,
        notes=status_data.get("notes"),
    )
    
    db.add(history)
    await db.commit()
    
    return {
        "id": str(order.id),
        "status": order.status,
        "updated_at": order.updated_at.isoformat(),
    }

