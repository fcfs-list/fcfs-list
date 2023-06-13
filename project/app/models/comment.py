""" Comment Model """
from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from . import Product, User

from .base_table import BaseTableModel, make_optional

class CommentBase(SQLModel):
    product_id: int = Field(foreign_key='products.id', index=True)
    user_id: int = Field(foreign_key='users.id')
    comment: str

class Comment(CommentBase, BaseTableModel, table=True):
    """Comment Model"""
    __tablename__ = "comments"

    # Relationships
    product: 'Product' = Relationship(back_populates='comments')
    user: 'User' = Relationship(back_populates='comments')

class CommentCreate(CommentBase):
    pass

class CommentRead(CommentBase):
    id: int

CommentUpdate = make_optional(CommentBase)
