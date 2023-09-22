from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Security
from starlette.status import (
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from app.auth import get_auth, confirm_auth_user
from app.db import get_session
from app.models.area import Area
from app.models.brand import Brand
from app.models.category import Category
from app.models.product import (
    Product,
    ProductCreate,
    ProductRead,
    ProductReadFull,
    ProductUpdate,
)
from app.models.product_area import ProductArea
from app.models.product_category import ProductCategory
from app.models.user import User
from app.utils.enums import ProductStatus
from fastapi_auth0 import Auth0User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


router = APIRouter()


# List
@router.get(
    "/",
    response_model=list[ProductRead],
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def list_products(
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["read:products"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["read:products"], session
    )  # Confirm permissions
    result = await session.execute(select(Product))
    products = result.scalars().unique().all()
    return products


# Detail
@router.get(
    "/{product_id}",
    response_model=ProductReadFull,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def get_product(
    product_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["read:products"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["read:products"], session
    )  # Confirm permissions
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Product not found")
    return product


# Insert
@router.post(
    "/",
    response_model=ProductReadFull,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def add_product(
    product: ProductCreate,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["write:products"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["write:products"], session
    )  # Confirm permissions
    if product.user_id is not None:
        user = await session.get(User, product.user_id)
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    if product.brand_id is not None:
        brand = await session.get(Brand, product.brand_id)
        if not brand:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Brand not found"
            )
    product = Product(**product.dict())
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


# Update
@router.patch(
    "/{product_id}",
    response_model=ProductReadFull,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Product not found")
    await confirm_auth_user(
        auth0_user, ["modify:products"], session, user_id=product.user_id
    )  # Confirm permissions
    update_data = payload.dict(exclude_unset=True)
    if "user_id" in update_data:
        user = await session.get(User, update_data["user_id"])
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    if "brand_id" in update_data:
        brand = await session.get(Brand, update_data["brand_id"])
        if not brand:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Brand not found"
            )
    for key, value in update_data.items():
        setattr(product, key, value)
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


# Delete
@router.delete(
    "/{product_id}",
    status_code=HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def delete_product(
    product_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Product not found")
    await confirm_auth_user(
        auth0_user, ["delete:products"], session, user_id=product.user_id
    )  # Confirm permissions
    # Soft delete
    update_data = {"status": ProductStatus.deleted, "deleted_at": datetime.utcnow()}
    for key, value in update_data.items():
        setattr(product, key, value)
    session.add(product)
    await session.commit()


## Product Areas ##


# Insert
@router.post(
    "/{product_id}/areas/{area_id}",
    response_model=ProductReadFull,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def add_product_area(
    product_id: int,
    area_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Product not found")
    await confirm_auth_user(
        auth0_user, ["modify:products"], session, user_id=product.user_id
    )  # Confirm permissions
    area = await session.get(Area, area_id)
    if not area:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Area not found")
    product_area = await session.execute(
        select(ProductArea)
        .where(ProductArea.product_id == product_id)
        .where(ProductArea.area_id == area_id)
    )
    product_area = product_area.scalars().all()
    if product_area:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="ProductArea already exists"
        )
    product_area = ProductArea(area_id=area_id, product_id=product_id)
    session.add(product_area)
    await session.commit()
    await session.refresh(product)
    return product


# Delete
@router.delete(
    "/{product_id}/areas/{area_id}",
    status_code=HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def delete_product_area(
    product_id: int,
    area_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    product_area = await session.execute(
        select(ProductArea)
        .where(ProductArea.product_id == product_id)
        .where(ProductArea.area_id == area_id)
    )
    product_area = product_area.scalars().first()
    if not product_area:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="ProductArea not found"
        )
    await confirm_auth_user(
        auth0_user, ["modify:products"], session, user_id=product_area.product.user_id
    )  # Confirm permissions
    await session.delete(product_area)
    await session.commit()


## Product Categories ##


# Insert
@router.post(
    "/{product_id}/categories/{category_id}",
    response_model=ProductReadFull,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def add_product_category(
    product_id: int,
    category_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Product not found")
    await confirm_auth_user(
        auth0_user, ["modify:products"], session, user_id=product.user_id
    )  # Confirm permissions
    category = await session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Category not found")
    product_category = await session.execute(
        select(ProductCategory)
        .where(ProductCategory.product_id == product_id)
        .where(ProductCategory.category_id == category_id)
    )
    product_category = product_category.scalars().all()
    if product_category:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="ProductCategory already exists"
        )
    product_category = ProductCategory(category_id=category_id, product_id=product_id)
    session.add(product_category)
    await session.commit()
    await session.refresh(product)
    return product


# Delete
@router.delete(
    "/{product_id}/categories/{category_id}",
    status_code=HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def delete_product_category(
    product_id: int,
    category_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    product_category = await session.execute(
        select(ProductCategory)
        .where(ProductCategory.product_id == product_id)
        .where(ProductCategory.category_id == category_id)
    )
    product_category = product_category.scalars().first()
    if not product_category:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="ProductCategory not found"
        )
    await confirm_auth_user(
        auth0_user,
        ["modify:products"],
        session,
        user_id=product_category.product.user_id,
    )  # Confirm permissions
    await session.delete(product_category)
    await session.commit()
