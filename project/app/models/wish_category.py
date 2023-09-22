""" WishCategory Model """
from sqlmodel import Field, Index, SQLModel, UniqueConstraint

from .base_table import BaseTableModel, make_optional


class WishCategoryBase(SQLModel):
    wish_id: int = Field(foreign_key="wishes.id")
    category_id: int = Field(foreign_key="categories.id")


class WishCategory(WishCategoryBase, BaseTableModel, table=True):
    """WishCategory Model"""

    __tablename__ = "wish_categories"
    __table_args__ = (
        UniqueConstraint("wish_id", "category_id"),
        Index(
            "ix_wish_categories_wish_id_category_id",
            "wish_id",
            "category_id",
            unique=True,
        ),
    )


class WishCategoryCreate(WishCategoryBase):
    pass


class WishCategoryRead(WishCategoryBase):
    id: int


WishCategoryUpdate = make_optional(WishCategoryBase)
