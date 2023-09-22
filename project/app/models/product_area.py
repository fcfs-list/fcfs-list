""" ProductArea Model """
from sqlmodel import Field, Index, SQLModel, UniqueConstraint

from .base_table import BaseTableModel, make_optional


class ProductAreaBase(SQLModel):
    product_id: int = Field(foreign_key="products.id")
    area_id: int = Field(foreign_key="areas.id")


class ProductArea(ProductAreaBase, BaseTableModel, table=True):
    """ProductArea Model"""

    __tablename__ = "product_areas"
    __table_args__ = (
        UniqueConstraint("product_id", "area_id"),
        Index(
            "ix_product_areas_product_id_area_id", "product_id", "area_id", unique=True
        ),
    )


class ProductAreaCreate(ProductAreaBase):
    pass


class ProductAreaRead(ProductAreaBase):
    id: int


ProductAreaUpdate = make_optional(ProductAreaBase)
