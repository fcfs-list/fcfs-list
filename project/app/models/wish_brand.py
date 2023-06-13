""" WishBrand Model """
from sqlmodel import Field, SQLModel, UniqueConstraint, Index

from .base_table import BaseTableModel, make_optional


class WishBrandBase(SQLModel):
    wish_id: int = Field(foreign_key='wishes.id')
    brand_id: int = Field(foreign_key='brands.id')

class WishBrand(WishBrandBase, BaseTableModel, table=True):
    """WishBrand Model"""
    __tablename__ = 'wish_brands'
    __table_args__ = (
        UniqueConstraint('wish_id', 'brand_id'),
        Index('ix_wish_brands_wish_id_brand_id', 'wish_id', 'brand_id')
    )

class WishBrandCreate(WishBrandBase):
    pass

class WishBrandRead(WishBrandBase):
    id: int

WishBrandUpdate = make_optional(WishBrandBase)
