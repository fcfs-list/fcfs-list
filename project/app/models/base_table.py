""" Base Model """
from datetime import datetime
from functools import lru_cache
from typing import Optional, Type

from pydantic import BaseModel, create_model

import orjson
from app.utils.serialization import orjson_dumps
from sqlmodel import Field, SQLModel


class BaseTableModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


@lru_cache(maxsize=None)  # avoids creating many classes with same name
def make_optional(baseclass: Type[BaseModel]) -> Type[BaseModel]:
    # Extracts the fields and validators from the baseclass and make fields optional
    fields = baseclass.__fields__
    validators = {"__validators__": baseclass.__validators__}
    optional_fields = {
        key: (Optional[item.type_], None) for key, item in fields.items()
    }
    return create_model(
        f"{baseclass.__name__}Optional", **optional_fields, __validators__=validators
    )
