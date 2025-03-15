import pytest
from unittest.mock import MagicMock, patch
from unittest.mock import AsyncMock
from backend.orders_service.app.schemas import (
    CreateOrderRequest,
    UpdatePartialOrderRequest,
)
from backend.orders_service.Core.redis_client import redis_client
from sqlalchemy.ext.asyncio import AsyncSession
from backend.common.Models import Orders
from backend.common.Models.Orders import OrderStatus
from backend.common.logger import logger
from backend.orders_service.app import utils, elastic_crud, crud
from backend.orders_service.app.services import *
from fastapi import HTTPException
import json
from unittest.mock import AsyncMock


@pytest.fixture(scope="module")
def mock_redis():
    """Фикстура для мокирования клиента Redis с асинхронной функцией delete"""
    with patch.object(
        redis_client, "delete", new_callable=AsyncMock
    ) as mock_delete, patch.object(
        redis_client, "set", new_callable=AsyncMock
    ) as mock_set, patch.object(
        redis_client, "get", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = '{"order_id": 1, "items": {}, "status": "в ожидании"}'
        yield mock_delete, mock_set, mock_get


@pytest.fixture(scope="module")
def mock_elasticsearch():
    """Фикстура для мокирования Elasticsearch клиента"""
    with patch.object(
        elastic_crud, "index_item", return_value=None
    ) as mock_index, patch.object(
        elastic_crud, "delete_item", new_callable=AsyncMock
    ) as mock_delete, patch.object(
        elastic_crud, "search_by_match_all", return_value=[]
    ), patch.object(
        elastic_crud, "search_by_term", return_value=[]
    ) as mock_search_by_term:
        yield mock_index, mock_delete, mock_search_by_term  # Возвращаем оба мока


@pytest.fixture(scope="module")
def mock_db_session():
    """Фикстура для мокирования сессии базы данных"""
    mock_session = AsyncMock(AsyncSession)
    yield mock_session


@pytest.mark.asyncio
async def test_add_order(mock_db_session, mock_redis, mock_elasticsearch):
    # Данные для создания заказа
    order_data = CreateOrderRequest(table_number=1, items={"Pizza": 10.0})

    # Мокируем create_order
    with patch.object(
        crud,
        "create_order",
        return_value=Orders(**order_data.model_dump(), status=OrderStatus.PENDING),
    ) as mock_create_order:
        result = await add_order(order=order_data, session=mock_db_session)

    # Проверка, что результат содержит статус PENDING
    assert result["status"] == OrderStatus.PENDING.value
    # # Проверка, что было удалено все из кэша
    mock_redis[0].assert_called_with("all_orders")
    # # Проверка, что индексирование в Elasticsearch было вызвано
    mock_elasticsearch[0].assert_called_with(doc=result, index="orders")


@pytest.mark.asyncio
async def test_delete_order(mock_db_session, mock_redis, mock_elasticsearch):
    order_id = 1
    with patch.object(crud, "delete_order_by_id", return_value=None), patch.object(
        elastic_crud, "delete_item", return_value=None
    ):
        await delete_order(order_id=order_id, session=mock_db_session)

    # mock_elasticsearch[1].assert_called_with(index="orders", item_id=order_id)
    mock_redis[0].assert_called_with("all_orders")


@pytest.mark.asyncio
async def test_calculate_revenue_general(mock_db_session):
    with patch.object(crud, "calculate_revenue_general", return_value=100.0):
        result = await calculate_revenue_general(session=mock_db_session)

    # Проверка, что функция вернула корректный доход
    assert result == 100.0


#
@pytest.mark.asyncio
async def test_update_order(mock_db_session, mock_redis, mock_elasticsearch):
    order_id = 1
    order_update = UpdatePartialOrderRequest(table_number=2, items={"Burger": 15.0})

    # Мокируем update_order
    with patch.object(
        crud,
        "update_order_by_id",
        return_value=Orders(
            **order_update.model_dump(exclude_none=True), status=OrderStatus.PENDING
        ),
    ):
        result = await update_order(
            order_id=order_id, order_update=order_update, session=mock_db_session
        )

    # Проверка, что обновленный заказ был возвращен
    assert result["status"] == OrderStatus.PENDING.value
    # Проверка, что обновление в Elasticsearch прошло успешно
    mock_elasticsearch[0].assert_called_with(doc=result, index="orders")
    # Проверка, что кэш был очищен
    mock_redis[0].assert_called_with("all_orders")


#
@pytest.mark.asyncio
async def test_get_all_orders(mock_db_session, mock_redis):
    orders_data = [
        Orders(id=i, table_number=1, status=OrderStatus.PENDING) for i in range(3)
    ]

    with patch.object(crud, "get_orders", return_value=orders_data):
        result = await get_all_orders(session=mock_db_session)

    # Проверка, что вернулись все заказы
    assert len(result) == 3
    # Проверка, что кэш был обновлен
    # mock_redis[2].assert_called_with(
    #     "all_orders", json.dumps([order.to_dict() for order in orders_data])
    # )


@pytest.mark.asyncio
async def test_search_orders_service(mock_redis, mock_elasticsearch):
    search_criteria = {"table_number": 1, "status": "в ожидании"}

    with patch.object(elastic_crud, "search_by_term", return_value=[]):
        result = await search_orders_service(**search_criteria)

    # Проверка, что запрос в Elasticsearch был сделан с нужными параметрами
    # mock_elasticsearch[2].assert_called_with("orders", **search_criteria)
    # Проверка, что результат поиска пуст
    assert result == []
