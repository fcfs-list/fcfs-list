""" Wish Model """
from typing import TYPE_CHECKING, List, Optional, Dict
from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_json import mutable_json_type

if TYPE_CHECKING:
    from . import User, Area, Brand, Category, Match

from .base_table import BaseTableModel, make_optional
from .brand import BrandRead
from .category import CategoryRead
from .wish_area import WishArea
from .wish_brand import WishBrand
from .wish_category import WishCategory


class WishBase(SQLModel):
    user_id: int = Field(foreign_key='users.id', index=True)
    keywords: str
    details: Optional[Dict] = Field(sa_column=Column(mutable_json_type(dbtype=JSONB, nested=True)), default=None)

class Wish(WishBase, BaseTableModel, table=True):
    """Wish Model"""
    __tablename__ = 'wishes'

    # Relationships
    user: 'User' = Relationship(back_populates='wishes')
    matches: List['Match'] = Relationship(back_populates='wish')
    areas: List['Area'] = Relationship(back_populates='wishes', link_model=WishArea)
    brands: List['Brand'] = Relationship(sa_relationship_kwargs={'lazy': 'joined'}, back_populates='wishes', link_model=WishBrand)
    categories: List['Category'] = Relationship(sa_relationship_kwargs={'lazy': 'joined'}, back_populates='wishes', link_model=WishCategory)

class WishCreate(WishBase):
    pass

class WishRead(WishBase):
    id: int

class WishReadFull(WishRead):
    brands: List[BrandRead] = []
    categories: List[CategoryRead] = []

WishUpdate = make_optional(WishBase)
