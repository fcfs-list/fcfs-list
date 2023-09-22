""" Brand Model """
from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

from .base_table import BaseTableModel, make_optional
from .wish_brand import WishBrand


if TYPE_CHECKING:
    from . import Product, Wish



class BrandBase(SQLModel):
    name_en: str = Field(index=True)
    name_ja: str = Field(index=True)


class Brand(BrandBase, BaseTableModel, table=True):
    """Brand Model"""

    __tablename__ = "brands"
    __table_args__ = (UniqueConstraint("name_en", "name_ja"),)

    # Relationships
    products: List["Product"] = Relationship(back_populates="brand")
    wishes: List["Wish"] = Relationship(back_populates="brands", link_model=WishBrand)


class BrandCreate(BrandBase):
    pass


class BrandRead(BrandBase):
    id: int


BrandUpdate = make_optional(BrandBase)
