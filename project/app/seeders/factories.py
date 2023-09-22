from decimal import Decimal
from random import choice
from typing import Any

from babel import numbers as bn

from app.models import Product, User
from pydantic_factories import (
    AsyncPersistenceProtocol,
    ModelFactory,
    SyncPersistenceProtocol,
    Use,
)


CURRENCIES = list(bn.list_currencies())


class SyncPersistenceHandler(SyncPersistenceProtocol):
    def save(self, data: Any, *args: Any, **kwargs: Any) -> Any:
        return data.dict()

    def save_many(self, data: Any, *args: Any, **kwargs: Any) -> Any:
        return [obj.dict() for obj in data]


class AsyncPersistenceHandler(AsyncPersistenceProtocol):
    async def save(self, data: Any, *args: Any, **kwargs: Any) -> Any:
        return data.dict()

    async def save_many(self, data: Any, *args: Any, **kwargs: Any) -> Any:
        return [obj.dict() for obj in data]


class FactoryBase(ModelFactory):
    __sync_persistence__ = SyncPersistenceHandler
    __async_persistence__ = AsyncPersistenceHandler


class UserFactory(FactoryBase):
    __model__ = User

    name = "Placeholder"
    email = "placeholder@email.com"


class ProductFactory(FactoryBase):
    __model__ = Product

    user_id = Use(choice, list(range(1, 6)))
    title = "Placeholder"
    description = "Placeholder"
    price = Use(choice, [Decimal(i) for i in range(0, 50000)])
    currency = Use(choice, CURRENCIES)
    brand_id = Use(choice, list(range(1, 8195)))
