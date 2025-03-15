from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import CreateOrderRequest, OrdersResponse, UpdatePartialOrderRequest
from . import services
from orders_service.Core.database import database

router = APIRouter(tags=["Orders"])


@router.post("/", response_model=OrdersResponse)
async def create_order(
    order: CreateOrderRequest,
    session: AsyncSession = Depends(database.get_async_session),
):
    """
    Создание нового заказа с расчетом общей стоимости и статусом "в ожидании".
    """
    return await services.add_order(order=order, session=session)


@router.delete("/{order_id}", status_code=201, response_model=dict)
async def delete_order(
    order_id: int, session: AsyncSession = Depends(database.get_async_session)
):
    """
    Удаление заказа по ID.
    """
    await services.delete_order(order_id=order_id, session=session)
    return {"detail": f"Order with id={order_id} deleted"}


@router.get("/search", response_model=list[OrdersResponse])
async def search_orders(
    table_number: int | None = Query(None, description="Номер стола для поиска"),
    status: str | None = Query(None, description="Статус для поиска"),
):
    """
    Поиск заказов по номеру стола и/или статусу.
    """
    return await services.search_orders_service(
        table_number=table_number, status=status
    )


@router.get("/", response_model=list[OrdersResponse])
async def get_all_orders(
    limit: int = 100,
    skip: int = 0,
    session: AsyncSession = Depends(database.get_async_session),
):
    """
    Получение всех заказов с пагинацией.
    """
    orders = await services.get_all_orders(session=session, limit=limit, skip=skip)
    return orders


@router.put("/{order_id}", response_model=OrdersResponse)
async def update_order_status(
    order_id: int,
    order_update: UpdatePartialOrderRequest,
    session: AsyncSession = Depends(database.get_async_session),
):
    """
    Обновление статуса заказа по ID.
    """
    return await services.update_order(
        order_id=order_id, order_update=order_update, session=session
    )


@router.get("/revenue", response_model=float)
async def calculate_revenue(
    session: AsyncSession = Depends(database.get_async_session),
):
    """
    Расчет общей выручки за заказы со статусом "оплачено".
    """
    revenue = await services.calculate_revenue_general(session=session)
    return revenue
