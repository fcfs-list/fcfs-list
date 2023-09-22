"""seed areas, brands, categories, products and users tables

Revision ID: f00112fd2e0a
Revises: 6508aeffb3ae
Create Date: 2023-01-23 07:46:09.806067

"""
import os
from datetime import datetime

from alembic import op
from app.seeders.area_table_seeder import seed_area_table
from app.seeders.brand_table_seeder import seed_brand_table
from app.seeders.category_table_seeder import seed_category_table_clothing
from app.seeders.product_table_seeder import seed_product_table
from app.seeders.user_table_seeder import seed_user_table
from sqlalchemy import MetaData, Table


# revision identifiers, used by Alembic.
revision = "f00112fd2e0a"
down_revision = "6508aeffb3ae"
branch_labels = None
depends_on = None


def upgrade() -> None:
    meta = MetaData(bind=op.get_bind())
    meta.reflect(
        only=(
            "brands",
            "areas",
            "categories",
            "users",
            "products",
        )
    )

    # Seed brands table
    brands_table = Table("brands", meta)
    brands = seed_brand_table()
    for i in range(len(brands)):
        brands[i]["created_at"] = datetime.now()
        brands[i]["updated_at"] = datetime.now()
    op.bulk_insert(brands_table, brands)
    op.execute(
        """SELECT setval('brands_id_seq', COALESCE((SELECT MAX(id)+1 FROM brands), 1), false);"""
    )

    # Seed areas table
    areas_table = Table("areas", meta)
    areas = seed_area_table()
    for i in range(len(areas)):
        if not areas[i].get("id"):
            areas[i]["id"] = i + 1
        areas[i]["created_at"] = datetime.now()
        areas[i]["updated_at"] = datetime.now()
    op.bulk_insert(areas_table, areas, multiinsert=False)
    op.execute(
        """SELECT setval('areas_id_seq', COALESCE((SELECT MAX(id)+1 FROM areas), 1), false);"""
    )

    # Seed categories table
    categories_table = Table("categories", meta)
    categories = seed_category_table_clothing()
    for i in range(len(categories)):
        categories[i]["created_at"] = datetime.now()
        categories[i]["updated_at"] = datetime.now()
    op.bulk_insert(categories_table, categories, multiinsert=False)
    op.execute(
        """SELECT setval('categories_id_seq', COALESCE((SELECT MAX(id)+1 FROM categories), 1), false);"""
    )

    if os.environ.get("ENV", "develop") == "develop":
        # Seed users table
        users_table = Table("users", meta)
        users = seed_user_table()
        op.bulk_insert(users_table, users)
        op.execute(
            """SELECT setval('users_id_seq', COALESCE((SELECT MAX(id)+1 FROM users), 1), false);"""
        )

        # Seed products table
        products_table = Table("products", meta)
        products = seed_product_table()
        op.bulk_insert(products_table, products)
        op.execute(
            """SELECT setval('products_id_seq', COALESCE((SELECT MAX(id)+1 FROM products), 1), false);"""
        )


def downgrade() -> None:
    pass
