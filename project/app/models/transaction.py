""" Transaction Model """
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel, Column, String
from sqlalchemy_utils import ChoiceType

from app.utils.enums import TransactionStatus
if TYPE_CHECKING:
    from . import TransactionMessage, User, Product

from .base_table import BaseTableModel, make_optional
from .transaction_message import TransactionMessageRead


class TransactionBase(SQLModel):
    product_id: int = Field(foreign_key='products.id')
    buyer_id: int = Field(foreign_key='users.id')
    status: TransactionStatus = Field(sa_column=Column(ChoiceType(TransactionStatus, impl=String())), default=TransactionStatus.created)

class Transaction(TransactionBase, BaseTableModel, table=True):
    """Transaction Model"""
    __tablename__ = 'transactions'

    deleted_at: Optional[datetime] = None

    # Relationships
    messages: List['TransactionMessage'] = Relationship(sa_relationship_kwargs={'lazy': 'joined'}, back_populates='transaction')
    # Relationships
    buyer: 'User' = Relationship(
        sa_relationship_kwargs={'primaryjoin': 'Transaction.buyer_id==User.id'},
        back_populates='transactions'
    )
    product: 'Product' = Relationship(back_populates='transactions')

class TransactionCreate(TransactionBase):
    pass

class TransactionRead(TransactionBase):
    id: int

class TransactionReadFull(TransactionRead):
    messages: List[TransactionMessageRead] = []

TransactionUpdate = make_optional(TransactionBase)
