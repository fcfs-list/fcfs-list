""" Image Model """
from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from . import Product

from .base_table import BaseTableModel, make_optional

class ImageBase(SQLModel):
    url: str
    order: int
    product_id: int = Field(foreign_key='products.id', index=True)

class Image(ImageBase, BaseTableModel, table=True):
    """Image Model"""
    __tablename__ = 'images'

    # Relationships
    product: 'Product' = Relationship(back_populates='images')

class ImageCreate(ImageBase):
    pass

class ImageRead(ImageBase):
    id: int

ImageUpdate = make_optional(ImageBase)
