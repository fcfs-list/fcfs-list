""" ProductCategory Model """
from sqlmodel import Field, SQLModel, UniqueConstraint, Index

from .base_table import BaseTableModel, make_optional


class ProductCategoryBase(SQLModel):
    product_id: int = Field(foreign_key='products.id')
    category_id: int = Field(foreign_key='categories.id')

class ProductCategory(ProductCategoryBase, BaseTableModel, table=True):
    """ProductCategory Model"""
    __tablename__ = 'product_categories'
    __table_args__ = (
        UniqueConstraint('product_id', 'category_id'),
        Index('ix_product_categories_product_id_category_id', 'product_id', 'category_id')
    )

class ProductCategoryCreate(ProductCategoryBase):
    pass

class ProductCategoryRead(ProductCategoryBase):
    id: int

ProductCategoryUpdate = make_optional(ProductCategoryBase)
