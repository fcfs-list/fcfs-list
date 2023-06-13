from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from app.db import get_session
from app.models.brand import Brand, BrandCreate, BrandUpdate, BrandRead

router = APIRouter()

# List
@router.get('/', response_model=list[BrandRead])
async def list_brands(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Brand))
    brands = result.scalars().all()
    return brands

# Detail
@router.get('/{brand_id}', response_model=BrandRead)
async def get_brand(brand_id: int, session: AsyncSession = Depends(get_session)):
    brand = await session.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Brand not found')
    return brand

# Insert
@router.post('/', response_model=BrandRead)
async def add_brand(brand: BrandCreate, session: AsyncSession = Depends(get_session)):
    existing_brand = await session.execute(select(Brand).where(
        Brand.name_en == brand.name_en).where(Brand.name_ja == brand.name_ja))
    existing_brand = existing_brand.scalars().all()
    if existing_brand:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='The given brand already exists')
    brand = Brand(**brand.dict())
    session.add(brand)
    await session.commit()
    await session.refresh(brand)
    return brand

# Update
@router.patch('/{brand_id}', response_model=BrandRead)
async def update_brand(brand_id: int, payload: BrandUpdate, session: AsyncSession = Depends(get_session)):
    brand = await session.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Brand not found')
    update_data = payload.dict(exclude_unset=True)
    if 'name_en' in update_data or 'name_ja' in update_data:
        existing_brand = await session.execute(select(Brand).where(
            Brand.name_en == update_data.get('name_en', brand.name_en)).where(
                Brand.name_ja == update_data.get('name_ja', brand.name_ja)))
        existing_brand = existing_brand.scalars().all()
        if existing_brand:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='The given brand already exists')
    for key, value in update_data.items():
        setattr(brand, key, value)
    session.add(brand)
    await session.commit()
    await session.refresh(brand)
    return brand


# Delete
@router.delete('/{brand_id}', status_code=HTTP_204_NO_CONTENT)
async def delete_brand(brand_id: int, session: AsyncSession = Depends(get_session)):
    brand = await session.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Brand not found')
    await session.delete(brand)
    await session.commit()
