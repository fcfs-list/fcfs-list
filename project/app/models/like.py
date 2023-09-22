""" Like Model """
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from .base_table import BaseTableModel, make_optional


if TYPE_CHECKING:
    from . import Product, User



class LikeBase(SQLModel):
    product_id: int = Field(foreign_key="products.id", index=True)
    user_id: int = Field(foreign_key="users.id")


class Like(LikeBase, BaseTableModel, table=True):
    """Like Model"""

    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint("user_id", "product_id"),)

    # Relationships
    product: "Product" = Relationship(back_populates="likes")
    user: "User" = Relationship(back_populates="likes")


class LikeCreate(LikeBase):
    pass


class LikeRead(LikeBase):
    id: int


LikeUpdate = make_optional(LikeBase)
