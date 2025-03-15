from pydantic import BaseModel, ConfigDict
from common.Models.Orders import OrderStatus


class CreateOrderRequest(BaseModel):
    table_number: int
    items: dict[str, float]  # список блюд

    model_config = ConfigDict(from_attributes=True)


class CreateOrderResponse(BaseModel):
    order_id: int
    total_price: float
    status: str

    model_config = ConfigDict(from_attributes=True)


class DeleteOrderRequest(BaseModel):
    order_id: int


class UpdatePartialOrderRequest(BaseModel):
    items: dict[str, float] | None = None
    status: OrderStatus | None = None


class OrdersResponse(BaseModel):
    id: int
    table_number: int
    items: dict | None | str
    status: OrderStatus
    total_price: float

    model_config = ConfigDict(from_attributes=True)
