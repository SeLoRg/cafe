import json

from orders_service.Core.database import database
from orders_service.Core.config import settings

from sqlalchemy import delete, Result, select, and_, func, update
from sqlalchemy.exc import SQLAlchemyError
from common.Models import Orders
from common.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult
from .schemas import OrderStatus, CreateOrderRequest
from . import utils


async def create_order(data: dict, session: AsyncSession) -> Orders:
    try:
        order = Orders(**data)
        session.add(order)

        await session.flush()
        await session.refresh(order)

        return order
    except SQLAlchemyError as e:
        print(f"Error creating order: {e}")
        raise


async def get_orders(
    session: AsyncSession, limit: int = 100, skip: int = 0
) -> list[Orders]:
    try:
        stmt = select(Orders).limit(limit=limit).offset(skip)
        res: Result = await session.execute(stmt)
        orders: list[Orders] = list(res.scalars().all())
        return orders
    except SQLAlchemyError as e:
        print(f"Error getting orders: {e}")
        raise


async def get_orders_by_filter(
    session: AsyncSession, limit: int = 0, skip: int = 0, **filters
) -> list[Orders]:
    try:
        filter_conditions = [
            getattr(Orders, key) == value for key, value in filters.items()
        ]
        stmt = select(Orders).limit(limit).offset(skip)

        if filter_conditions:
            stmt = stmt.filter(*filter_conditions)

        res: Result = await session.execute(stmt)
        orders: list[Orders] = list(res.scalars().all())
        return orders
    except SQLAlchemyError as e:
        print(f"Error getting orders: {e}")
        raise


async def update_order_by_id(
    session: AsyncSession, order_id: int, **update_fields
) -> Orders:
    try:
        if not update_fields:
            raise ValueError("No fields provided for update.")

        if "items" in update_fields:
            update_fields["items"] = json.dumps(update_fields["items"])

        stmt = (
            update(Orders)
            .where(Orders.id == order_id)
            .values(**update_fields)
            .returning(Orders)
        )

        result: Result = await session.execute(stmt)
        updated_order: Orders | None = result.scalars().one_or_none()

        if updated_order is None:
            raise ValueError(f"Order with id {order_id} not found.")

        updated_order.total_price = utils.revenue_calculate_to_order(
            json.loads(updated_order.items)
        )

        await session.flush()
        await session.refresh(updated_order)
        return updated_order

    except SQLAlchemyError as e:
        print(f"Database error during order update: {e}")
        raise

    except Exception as e:
        print(f"Error updating order: {e}")
        raise


async def delete_order_by_id(order_id: int, session: AsyncSession) -> None:
    try:
        stmt = delete(Orders).where(Orders.id == order_id)
        await session.execute(stmt)
    except SQLAlchemyError as e:
        print(f"Error deleting order: {e}")
        raise


async def calculate_revenue_general(session: AsyncSession) -> float:
    stmt = select(func.sum(Orders.total_price)).where(Orders.status == OrderStatus.PAID)
    res = await session.execute(stmt)
    # logger.info(f"{res.scalar()}")
    total_revenue = res.scalar() or 0.0
    return total_revenue
