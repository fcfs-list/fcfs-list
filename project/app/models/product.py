""" Product Model """
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Dict, List, Optional

from babel import numbers as bn
from pydantic import validator

from app.utils.enums import (
    ProductCondition,
    ProductStatus,
    SellOrLend,
    SizeType,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_json import mutable_json_type
from sqlalchemy_utils import ChoiceType
from sqlmodel import Column, Field, Relationship, SQLModel, String

from .area import AreaRead
from .base_table import BaseTableModel, make_optional
from .brand import BrandRead
from .category import CategoryRead
from .comment import CommentRead
from .image import ImageRead
from .like import LikeRead
from .match import MatchRead
from .offer import OfferRead
from .product_area import ProductArea
from .product_category import ProductCategory
from .transaction import TransactionRead
from .user import UserRead


if TYPE_CHECKING:
    from . import (
        User,
        Comment,
        Like,
        Match,
        Image,
        Offer,
        Transaction,
        Category,
        Area,
        Brand,
    )


CURRENCIES = bn.list_currencies()
CURRENCY_VALUE_ERROR = ValueError(
    "Invalid currency code submitted. "
    f"Value must be one of the following {', '.join(CURRENCIES)}."
)


class ProductBase(SQLModel):
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str
    description: str
    price: Decimal = 0
    currency: Optional[str] = None
    condition: ProductCondition = Field(
        sa_column=Column(ChoiceType(ProductCondition, impl=String()))
    )
    sell_or_lend: Optional[SellOrLend] = Field(
        sa_column=Column(ChoiceType(SellOrLend, impl=String())), default=None
    )
    lend_period: Optional[int] = None
    status: ProductStatus = Field(
        sa_column=Column(ChoiceType(ProductStatus, impl=String())),
        default=ProductStatus.draft,
    )
    size_type: Optional[SizeType] = Field(
        sa_column=Column(ChoiceType(SizeType, impl=String())), default=None
    )
    size: Optional[str] = None
    brand_id: Optional[int] = Field(foreign_key="brands.id", default=None)
    immediate_deal: bool = True
    negotiable: bool = False
    match_deadline: int = 48  # In hours
    details: Optional[Dict] = Field(
        sa_column=Column(mutable_json_type(dbtype=JSONB, nested=True)), default=None
    )

    @validator("price")
    def positive_price(cls: SQLModel, v: Decimal) -> Decimal:
        if v and v <= 0:
            raise ValueError("Amount must be a positive number.")
        return v

    @validator("currency")
    def valid_currency(cls: SQLModel, v: str) -> str:
        if v not in CURRENCIES:
            raise CURRENCY_VALUE_ERROR
        return v


class Product(ProductBase, BaseTableModel, table=True):
    """Product Model"""

    __tablename__ = "products"

    deleted_at: Optional[datetime] = None

    # Relationships
    user: "User" = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}, back_populates="products"
    )
    brand: Optional["Brand"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}, back_populates="products"
    )
    comments: List["Comment"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}, back_populates="product"
    )
    likes: List["Like"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}, back_populates="product"
    )
    matches: List["Match"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}, back_populates="product"
    )
    images: List["Image"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}, back_populates="product"
    )
    offers: List["Offer"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}, back_populates="product"
    )
    transactions: List["Transaction"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}, back_populates="product"
    )
    categories: List["Category"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"},
        back_populates="products",
        link_model=ProductCategory,
    )
    areas: List["Area"] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"},
        back_populates="products",
        link_model=ProductArea,
    )


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int


class ProductReadFull(ProductRead):
    user: UserRead
    brand: Optional[BrandRead] = None
    comments: List[CommentRead] = []
    likes: List[LikeRead] = []
    matches: List[MatchRead] = []
    images: List[ImageRead] = []
    offers: List[OfferRead] = []
    transactions: List[TransactionRead] = []
    categories: List[CategoryRead] = []
    areas: List[AreaRead] = []


ProductUpdate = make_optional(ProductBase)
