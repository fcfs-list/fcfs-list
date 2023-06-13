""" UserArea Model """
from sqlmodel import Field, SQLModel, UniqueConstraint, Index

from .base_table import BaseTableModel, make_optional


class UserAreaBase(SQLModel):
    user_id: int = Field(foreign_key='users.id')
    area_id: int = Field(foreign_key='areas.id')

class UserArea(UserAreaBase, BaseTableModel, table=True):
    """UserArea Model"""
    __tablename__ = 'user_areas'
    __table_args__ = (
        UniqueConstraint('user_id', 'area_id'),
        Index('ix_user_areas_user_id_area_id', 'user_id', 'area_id')
    )

class UserAreaCreate(UserAreaBase):
    pass

class UserAreaRead(UserAreaBase):
    id: int

UserAreaUpdate = make_optional(UserAreaBase)
