from .Base import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.inspection import inspect
from sqlalchemy import JSON, Enum
from enum import Enum as PyEnum
import json


class OrderStatus(PyEnum):
    READY = "готово"
    PENDING = "в ожидании"
    PAID = "оплачено"

    @classmethod
    def get_name_by_value(cls, value: str | None) -> str | None:
        if value is None:
            return None
        for status in cls:
            if status.value == value:
                return status.name
        raise ValueError(f"Invalid status value: {value}")


class Orders(Base):
    __tablename__ = "Orders"
    table_number: Mapped[int] = mapped_column(nullable=False)
    items = mapped_column(JSON, default=dict, nullable=False)
    total_price: Mapped[float] = mapped_column(nullable=False, default=0.0)
    status = mapped_column(Enum(OrderStatus), nullable=False)

    def __repr__(self):
        return f"<Order(id={self.id}, table_number={self.table_number}, status='{self.status}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "table_number": self.table_number,
            "items": self.items,
            "total_price": self.total_price,
            "status": self.status.value,
        }
