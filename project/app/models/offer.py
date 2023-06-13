""" Offer Model """
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel, Column, String
from sqlalchemy_utils import ChoiceType

from app.utils.enums import OfferStatus
if TYPE_CHECKING:
    from . import Product, User

from .base_table import BaseTableModel, make_optional


class OfferBase(SQLModel):
    product_id: int = Field(foreign_key='products.id')
    user_id: int = Field(foreign_key='users.id')
    amount: float
    order: Optional[int]
    status: OfferStatus = Field(sa_column=Column(ChoiceType(OfferStatus, impl=String())), default=OfferStatus.created)
    deadline: Optional[datetime]

class Offer(OfferBase, BaseTableModel, table=True):
    """Offer Model"""
    __tablename__ = 'offers'

    # Relationships
    product: 'Product' = Relationship(back_populates='offers')
    user: 'User' = Relationship(back_populates='offers')

class OfferCreate(OfferBase):
    pass

class OfferRead(OfferBase):
    id: int

OfferUpdate = make_optional(OfferBase)
