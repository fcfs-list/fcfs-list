""" Match Model """
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel, Column, String, UniqueConstraint
from sqlalchemy_utils import ChoiceType

from app.utils.enums import MatchStatus
if TYPE_CHECKING:
    from . import Product, User, Wish, MatchMessage

from .base_table import BaseTableModel, make_optional
from .match_message import MatchMessageRead


class MatchBase(SQLModel):
    product_id: int = Field(foreign_key='products.id', index=True)
    user_id: int = Field(foreign_key='users.id', index=True)
    wish_id: Optional[int] = Field(foreign_key='wishes.id', default=None)
    order: Optional[int]
    status: MatchStatus = Field(sa_column=Column(ChoiceType(MatchStatus, impl=String())), default=MatchStatus.created)
    deadline: Optional[datetime]

class Match(MatchBase, BaseTableModel, table=True):
    """Match Model"""
    __tablename__ = 'matches'
    __table_args__ = (
        UniqueConstraint('user_id', 'product_id'),
    )

    # Relationships
    product: 'Product' = Relationship(back_populates='matches')
    user: 'User' = Relationship(back_populates='matches')
    wish: Optional['Wish'] = Relationship(back_populates='matches')
    messages: List['MatchMessage'] = Relationship(sa_relationship_kwargs={'lazy': 'joined'}, back_populates='match')


class MatchCreate(MatchBase):
    pass

class MatchRead(MatchBase):
    id: int

class MatchReadFull(MatchRead):
    messages: List[MatchMessageRead] = []

MatchUpdate = make_optional(MatchBase)
