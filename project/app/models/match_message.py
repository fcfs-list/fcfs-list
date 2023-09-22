""" MatchMessage Model """
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from .base_table import BaseTableModel, make_optional


if TYPE_CHECKING:
    from . import Match, User



class MatchMessageBase(SQLModel):
    match_id: int = Field(foreign_key="matches.id", index=True)
    user_id: int = Field(foreign_key="users.id")
    content: str


class MatchMessage(MatchMessageBase, BaseTableModel, table=True):
    """MatchMessage Model"""

    __tablename__ = "match_messages"

    deleted_at: Optional[datetime] = None

    # Relationships
    match: "Match" = Relationship(back_populates="messages")
    user: "User" = Relationship(back_populates="match_messages")


class MatchMessageCreate(MatchMessageBase):
    pass


class MatchMessageRead(MatchMessageBase):
    id: int


MatchMessageUpdate = make_optional(MatchMessageBase)
