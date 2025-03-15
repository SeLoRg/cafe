from orders_service.app.schemas import CreateOrderRequest, UpdatePartialOrderRequest
from orders_service.Core.redis_client import redis_client
from sqlalchemy.ext.asyncio import AsyncSession
from common.Models import Orders
from common.Models.Orders import OrderStatus
from common import exceptions
from common.logger import logger
from . import utils, elastic_crud, crud
from fastapi import HTTPException
import json


@exceptions.exception_handler
async def add_order(order: CreateOrderRequest, session: AsyncSession) -> dict:
    logger.info(f"Добавление заказа в бд...")
    total_price: float = utils.revenue_calculate_to_order(order.items)
    data: dict = dict(
        **order.model_dump(), total_price=total_price, status=OrderStatus.PENDING
    )
    new_order: Orders = await crud.create_order(data=data, session=session)
    logger.info(f"Заказ создан и добавлен в бд")
    logger.info(f"Индексирование в elasticsearch...")
    await elastic_crud.index_item(
        doc=new_order.to_dict(), index=new_order.__tablename__.lower()
    )
    logger.info(f"Индексирование успешно завершилось")
    new_order_dict = new_order.to_dict()
    await session.commit()

    logger.info(f"Удаление старых записей из кэша...")
    await redis_client.delete("all_orders")
    logger.info(f"Записи удалены...")
    return new_order_dict


@exceptions.exception_handler
async def delete_order(order_id: int, session: AsyncSession):
    logger.info(f"Удаляем запись из бд...")
    await crud.delete_order_by_id(order_id=order_id, session=session)
    logger.info(f"Запись удалена")
    logger.info(f"Удаляем запись из elastic...")
    await elastic_crud.delete_item(Orders.__tablename__.lower(), item_id=order_id)
    logger.info(f"Запись удалена")

    await session.commit()

    logger.info(f"Удаление старых записей из кэша...")
    await redis_client.delete("all_orders")
    logger.info(f"Записи удалены...")


@exceptions.exception_handler
async def calculate_revenue_general(session: AsyncSession) -> float:
    return await crud.calculate_revenue_general(session=session)


@exceptions.exception_handler
async def update_order(
    order_id: int, order_update: UpdatePartialOrderRequest, session: AsyncSession
) -> dict:
    logger.info(f"Обновление заказа в бд: {order_update.model_dump()}...")
    updated_order: Orders = await crud.update_order_by_id(
        order_id=order_id, session=session, **order_update.model_dump(exclude_none=True)
    )

    updated_order_dict = updated_order.to_dict()
    if isinstance(updated_order_dict["items"], str):
        updated_order_dict["items"] = json.loads(updated_order_dict["items"])

    logger.info(f"Заказ обновлен: {updated_order_dict}")
    logger.info(f"Обновление заказа в elasticsearch...")
    await elastic_crud.delete_item(index=Orders.__tablename__.lower(), item_id=order_id)
    await elastic_crud.index_item(
        index=Orders.__tablename__.lower(), doc=updated_order_dict
    )
    logger.info(f"Заказ обновлен")
    await session.commit()

    logger.info(f"Удаление старых записей из кэша...")
    await redis_client.delete("all_orders")
    logger.info(f"Записи удалены...")

    return updated_order_dict


@exceptions.exception_handler
async def get_all_orders(
    session: AsyncSession, limit: int = 100, skip: int = 0
) -> list[Orders]:
    logger.info(f"Получение всех заказов из кэша...")
    cached_data = await redis_client.get("all_orders")

    if cached_data:
        logger.info(f"Заказы получены")
        return json.loads(cached_data)
    logger.info(f"Кэш пуст")
    logger.info(f"Получение всех заказов из бд...")
    orders = await crud.get_orders(session=session, limit=limit, skip=skip)
    logger.info(f"Заказы получены")

    logger.info("Обновление кэша...")
    await redis_client.set(
        "all_orders", json.dumps([order.to_dict() for order in orders])
    )
    logger.info(f"Кэш обновлен")

    return orders


@exceptions.exception_handler
async def search_orders_service(
    table_number: int | None = None, status: str | None = None
) -> list[dict]:
    terms = {}
    if table_number is not None:
        terms["table_number"] = table_number
    if status is not None:
        terms["status.keyword"] = status
    logger.info(f"Ищем совпадения {terms} в elastic...")

    if not terms:
        response = await elastic_crud.search_by_match_all(
            index=Orders.__tablename__.lower()
        )
    else:
        response = await elastic_crud.search_by_term(
            index=Orders.__tablename__.lower(), **terms
        )

    out = [hit["_source"] for hit in response]
    logger.info(f"Найдено: {out}")
    return out
