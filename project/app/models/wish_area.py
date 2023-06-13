""" WishArea Model """
from sqlmodel import Field, SQLModel, UniqueConstraint, Index

from .base_table import BaseTableModel, make_optional


class WishAreaBase(SQLModel):
    wish_id: int = Field(foreign_key='wishes.id')
    area_id: int = Field(foreign_key='areas.id')

class WishArea(WishAreaBase, BaseTableModel, table=True):
    """WishArea Model"""
    __tablename__ = 'wish_areas'
    __table_args__ = (
        UniqueConstraint('wish_id', 'area_id'),
        Index('ix_wish_areas_wish_id_area_id', 'wish_id', 'area_id')
    )

class WishAreaCreate(WishAreaBase):
    pass

class WishAreaRead(WishAreaBase):
    id: int

WishAreaUpdate = make_optional(WishAreaBase)
