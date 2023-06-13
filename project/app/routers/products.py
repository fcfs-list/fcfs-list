from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from app.db import get_session
from app.models.product import Product, ProductCreate, ProductUpdate, ProductRead, ProductReadFull
from app.models.user import User
from app.models.brand import Brand
from app.models.area import Area
from app.models.product_area import ProductArea
from app.models.category import Category
from app.models.product_category import ProductCategory

router = APIRouter()

# List
@router.get('/', response_model=list[ProductRead])
async def list_products(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Product))
    products = result.scalars().unique().all()
    return products

# Detail
@router.get('/{product_id}', response_model=ProductReadFull)
async def get_product(product_id: int, session: AsyncSession = Depends(get_session)):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Product not found')
    return product

# Insert
@router.post('/', response_model=ProductReadFull)
async def add_product(product: ProductCreate, session: AsyncSession = Depends(get_session)):
    if product.user_id is not None:
        user = await session.get(User, product.user_id)
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User not found')
    if product.brand_id is not None:
        brand = await session.get(Brand, product.brand_id)
        if not brand:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Brand not found')
    product = Product(**product.dict())
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product

# Update
@router.patch('/{product_id}', response_model=ProductReadFull)
async def update_product(product_id: int, payload: ProductUpdate, session: AsyncSession = Depends(get_session)):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Product not found')
    update_data = payload.dict(exclude_unset=True)
    if 'user_id' in update_data:
        user = await session.get(User, update_data['user_id'])
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User not found')
    if 'brand_id' in update_data:
        brand = await session.get(Brand, update_data['brand_id'])
        if not brand:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Brand not found')
    for key, value in update_data.items():
        setattr(product, key, value)
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


# Delete
@router.delete('/{product_id}', status_code=HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, session: AsyncSession = Depends(get_session)):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Product not found')
    await session.delete(product)
    await session.commit()


## Product Areas ##

# Insert
@router.post('/{product_id}/areas/{area_id}', response_model=ProductReadFull)
async def add_product_area(product_id: int, area_id: int, session: AsyncSession = Depends(get_session)):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Product not found')
    area = await session.get(Area, area_id)
    if not area:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Area not found')
    product_area = await session.execute(select(ProductArea).where(
            ProductArea.product_id == product_id).where(
                ProductArea.area_id == area_id))
    product_area = product_area.scalars().all()
    if product_area:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='ProductArea already exists')
    product_area = ProductArea(
        area_id=area_id,
        product_id=product_id
    )
    session.add(product_area)
    await session.commit()
    await session.refresh(product)
    return product

# Delete
@router.delete('/{product_id}/areas/{area_id}', status_code=HTTP_204_NO_CONTENT)
async def delete_product_area(product_id: int, area_id: int, session: AsyncSession = Depends(get_session)):
    product_area = await session.execute(select(ProductArea).where(
            ProductArea.product_id == product_id).where(
                ProductArea.area_id == area_id))
    product_area = product_area.scalars().first()
    if not product_area:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='ProductArea not found')
    await session.delete(product_area)
    await session.commit()


## Product Categories ##

# Insert
@router.post('/{product_id}/categories/{category_id}', response_model=ProductReadFull)
async def add_product_category(product_id: int, category_id: int, session: AsyncSession = Depends(get_session)):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Product not found')
    category = await session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Category not found')
    product_category = await session.execute(select(ProductCategory).where(
            ProductCategory.product_id == product_id).where(
                ProductCategory.category_id == category_id))
    product_category = product_category.scalars().all()
    if product_category:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='ProductCategory already exists')
    product_category = ProductCategory(
        category_id=category_id,
        product_id=product_id
    )
    session.add(product_category)
    await session.commit()
    await session.refresh(product)
    return product

# Delete
@router.delete('/{product_id}/categories/{category_id}', status_code=HTTP_204_NO_CONTENT)
async def delete_product_category(product_id: int, category_id: int, session: AsyncSession = Depends(get_session)):
    product_category = await session.execute(select(ProductCategory).where(
            ProductCategory.product_id == product_id).where(
                ProductCategory.category_id == category_id))
    product_category = product_category.scalars().first()
    if not product_category:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='ProductCategory not found')
    await session.delete(product_category)
    await session.commit()