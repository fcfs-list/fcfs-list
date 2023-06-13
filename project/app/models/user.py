""" User Model """
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel
from pydantic import EmailStr

if TYPE_CHECKING:
    from . import (
        Product, Wish, Like, Comment, Offer, Match,
        MatchMessage, Transaction, TransactionMessage, Area
    )

from .base_table import BaseTableModel, make_optional
from .area import AreaRead
from .like import LikeRead
from .offer import OfferRead
from .match import MatchRead
from .wish import WishRead
from .user_area import UserArea


class UserBase(SQLModel):
    name: str
    email: EmailStr = Field(index=True, unique=True)
    phone: Optional[str] = Field(index=True, unique=True, default=None)

class UserBaseWithAuth(UserBase):
    password: str
    # second_password: Optional[SecretStr] = None
    # api_token: Optional[SecretStr] = None
    # remember_token: Optional[SecretStr] = None
    is_admin: bool = False
    verified_at: datetime | None = None

class User(UserBaseWithAuth, BaseTableModel, table=True):
    """User Model."""
    __tablename__ = 'users'

    deleted_at: Optional[datetime] = None

    # Relationships
    products: List['Product'] = Relationship(back_populates='user')
    wishes: List['Wish'] = Relationship(sa_relationship_kwargs={'lazy': 'joined'}, back_populates='user')
    likes: List['Like'] = Relationship(sa_relationship_kwargs={'lazy': 'joined'}, back_populates='user')
    comments: List['Comment'] = Relationship(back_populates='user')
    offers: List['Offer'] = Relationship(sa_relationship_kwargs={'lazy': 'joined'}, back_populates='user')
    transactions: List['Transaction'] = Relationship(back_populates='buyer')
    transaction_messages: 'TransactionMessage' = Relationship(back_populates='user')
    matches: List['Match'] = Relationship(sa_relationship_kwargs={'lazy': 'joined'}, back_populates='user')
    match_messages: 'MatchMessage' = Relationship(back_populates='user')
    areas: List['Area'] = Relationship(sa_relationship_kwargs={'lazy': 'joined'}, back_populates='users', link_model=UserArea)
    areas_created: List['Area'] = Relationship(back_populates='author')

class UserCreate(UserBaseWithAuth):
    pass

class UserRead(UserBase):
    id: int

class UserReadFull(UserRead):
    areas: List[AreaRead] = []
    wishes: List[WishRead] = []
    likes: List[LikeRead] = []
    offers: List[OfferRead] = []
    matches: List[MatchRead] = []

UserUpdate = make_optional(UserBaseWithAuth)
