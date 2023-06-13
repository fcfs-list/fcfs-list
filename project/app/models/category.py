""" Category Model """
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    from . import Wish, Product

from .base_table import BaseTableModel, make_optional
from .wish_category import WishCategory
from .product_category import ProductCategory


class CategoryBase(SQLModel):
    parent_id: Optional[int] = Field(default=None, foreign_key='categories.id')
    level: int
    name_en: str = Field(index=True)
    description_en: Optional[str] = None
    name_ja: str = Field(index=True)
    description_ja: Optional[str] = None

class Category(CategoryBase, BaseTableModel, table=True):
    """Category Model"""
    __tablename__ = 'categories'
    __table_args__ = (
        UniqueConstraint('name_en', 'parent_id'),
    )

    # Relationships
    parent: Optional['Category'] = Relationship(
        sa_relationship_kwargs={'remote_side': 'Category.id', 'backref': 'children', 'lazy': 'selectin'}
    )
    wishes: List['Wish'] = Relationship(back_populates='categories', link_model=WishCategory)
    products: List['Product'] = Relationship(back_populates='categories', link_model=ProductCategory)

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int

class CategoryReadFull(CategoryRead):
    parent: Optional[CategoryRead] = None

CategoryUpdate = make_optional(CategoryBase)
