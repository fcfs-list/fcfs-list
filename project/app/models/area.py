""" Area Model """
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from .base_table import BaseTableModel, make_optional
from .product_area import ProductArea
from .user_area import UserArea
from .wish_area import WishArea


if TYPE_CHECKING:
    from . import Product, User, Wish



class AreaBase(SQLModel):
    name_en: str = Field(index=True)
    name_ja: str = Field(index=True)
    parent_id: Optional[int] = Field(default=None, foreign_key="areas.id")
    radius_km: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")


class Area(AreaBase, BaseTableModel, table=True):
    """Area Model"""

    __tablename__ = "areas"
    __table_args__ = (UniqueConstraint("name_en", "parent_id"),)

    # Relationships
    parent: "Area" = Relationship(
        sa_relationship_kwargs={
            "remote_side": "Area.id",
            "backref": "children",
            "lazy": "selectin",
        }
    )
    author: "User" = Relationship(
        sa_relationship_kwargs={"primaryjoin": "Area.created_by==User.id"},
        back_populates="areas",
    )
    products: List["Product"] = Relationship(
        back_populates="areas", link_model=ProductArea
    )
    users: List["User"] = Relationship(back_populates="areas", link_model=UserArea)
    wishes: List["Wish"] = Relationship(back_populates="areas", link_model=WishArea)


class AreaCreate(AreaBase):
    pass


class AreaRead(AreaBase):
    id: int


class AreaReadFull(AreaRead):
    parent: Optional[AreaRead] = None


AreaUpdate = make_optional(AreaBase)
