""" TransactionMessage Model """
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from .base_table import BaseTableModel, make_optional


if TYPE_CHECKING:
    from . import Transaction, User



class TransactionMessageBase(SQLModel):
    transaction_id: int = Field(foreign_key="transactions.id", index=True)
    user_id: int = Field(foreign_key="users.id")
    content: str


class TransactionMessage(TransactionMessageBase, BaseTableModel, table=True):
    """TransactionMessage Model"""

    __tablename__ = "transaction_messages"

    deleted_at: Optional[datetime] = None

    # Relationships
    transaction: "Transaction" = Relationship(back_populates="messages")
    user: "User" = Relationship(back_populates="transaction_messages")


class TransactionMessageCreate(TransactionMessageBase):
    pass


class TransactionMessageRead(TransactionMessageBase):
    id: int


TransactionMessageUpdate = make_optional(TransactionMessageBase)
