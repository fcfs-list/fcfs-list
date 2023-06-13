from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from app.db import get_session
from app.models.wish import Wish, WishCreate, WishUpdate, WishRead, WishReadFull
from app.models.wish import Wish
from app.models.user import User
from app.models.brand import Brand
from app.models.wish_brand import WishBrand
from app.models.area import Area
from app.models.wish_area import WishArea
from app.models.category import Category
from app.models.wish_category import WishCategory

router = APIRouter()

# List
@router.get('/', response_model=list[WishRead])
async def list_wishes(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Wish))
    wishes = result.scalars().unique().all()
    return wishes

# Detail
@router.get('/{wish_id}', response_model=WishReadFull)
async def get_wish(wish_id: int, session: AsyncSession = Depends(get_session)):
    wish = await session.get(Wish, wish_id)
    if not wish:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Wish not found')
    return wish

# Insert
@router.post('/', response_model=WishRead)
async def add_wish(new_wish: WishCreate, session: AsyncSession = Depends(get_session)):
    if new_wish.user_id is not None:
        user = await session.get(User, new_wish.user_id)
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User not found')
    new_wish = Wish(
        user_id=new_wish.user_id,
        keywords=new_wish.keywords,
        details=new_wish.details
    )
    session.add(new_wish)
    await session.commit()
    await session.refresh(new_wish)
    return new_wish

# Update
@router.patch('/{wish_id}', response_model=WishRead)
async def update_wish(wish_id: int, payload: WishUpdate, session: AsyncSession = Depends(get_session)):
    wish = await session.get(Wish, wish_id)
    if not wish:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Wish not found')
    update_data = payload.dict(exclude_unset=True)
    if 'user_id' in update_data:
        user = await session.get(User, update_data['user_id'])
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User not found')
    for key, value in update_data.items():
        setattr(wish, key, value)
    session.add(wish)
    await session.commit()
    await session.refresh(wish)
    return wish


# Delete
@router.delete('/{wish_id}', status_code=HTTP_204_NO_CONTENT)
async def delete_wish(wish_id: int, session: AsyncSession = Depends(get_session)):
    wish = await session.get(Wish, wish_id)
    if not wish:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Wish not found')
    await session.delete(wish)
    await session.commit()


## Wish Areas ##

# Insert
@router.post('/{wish_id}/areas/{area_id}', response_model=WishReadFull)
async def add_wish_area(wish_id: int, area_id: int, session: AsyncSession = Depends(get_session)):
    wish = await session.get(Wish, wish_id)
    if not wish:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Wish not found')
    area = await session.get(Area, area_id)
    if not area:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Area not found')
    wish_area = await session.execute(select(WishArea).where(
            WishArea.wish_id == wish_id).where(
                WishArea.area_id == area_id))
    wish_area = wish_area.scalars().all()
    if wish_area:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='WishArea already exists')
    wish_area = WishArea(
        area_id=area_id,
        wish_id=wish_id
    )
    session.add(wish_area)
    await session.commit()
    await session.refresh(wish)
    return wish

# Delete
@router.delete('/{wish_id}/areas/{area_id}', status_code=HTTP_204_NO_CONTENT)
async def delete_wish_area(wish_id: int, area_id: int, session: AsyncSession = Depends(get_session)):
    wish_area = await session.execute(select(WishArea).where(
            WishArea.wish_id == wish_id).where(
                WishArea.area_id == area_id))
    wish_area = wish_area.scalars().first()
    if not wish_area:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='WishArea not found')
    await session.delete(wish_area)
    await session.commit()


## Wish Categories ##

# Insert
@router.post('/{wish_id}/categories/{category_id}', response_model=WishReadFull)
async def add_wish_category(wish_id: int, category_id: int, session: AsyncSession = Depends(get_session)):
    wish = await session.get(Wish, wish_id)
    if not wish:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Wish not found')
    category = await session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Category not found')
    wish_category = await session.execute(select(WishCategory).where(
            WishCategory.wish_id == wish_id).where(
                WishCategory.category_id == category_id))
    wish_category = wish_category.scalars().all()
    if wish_category:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='WishCategory already exists')
    wish_category = WishCategory(
        category_id=category_id,
        wish_id=wish_id
    )
    session.add(wish_category)
    await session.commit()
    await session.refresh(wish)
    return wish

# Delete
@router.delete('/{wish_id}/categories/{category_id}', status_code=HTTP_204_NO_CONTENT)
async def delete_wish_category(wish_id: int, category_id: int, session: AsyncSession = Depends(get_session)):
    wish_category = await session.execute(select(WishCategory).where(
            WishCategory.wish_id == wish_id).where(
                WishCategory.category_id == category_id))
    wish_category = wish_category.scalars().first()
    if not wish_category:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='WishCategory not found')
    await session.delete(wish_category)
    await session.commit()


## Wish Brands ##

# Insert
@router.post('/{wish_id}/brands/{brand_id}', response_model=WishReadFull)
async def add_wish_brand(wish_id: int, brand_id: int, session: AsyncSession = Depends(get_session)):
    wish = await session.get(Wish, wish_id)
    if not wish:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Wish not found')
    brand = await session.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Brand not found')
    wish_brand = await session.execute(select(WishBrand).where(
            WishBrand.wish_id == wish_id).where(
                WishBrand.brand_id == brand_id))
    wish_brand = wish_brand.scalars().all()
    if wish_brand:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='WishBrand already exists')
    wish_brand = WishBrand(
        brand_id=brand_id,
        wish_id=wish_id
    )
    session.add(wish_brand)
    await session.commit()
    await session.refresh(wish)
    return wish

# Delete
@router.delete('/{wish_id}/brands/{brand_id}', status_code=HTTP_204_NO_CONTENT)
async def delete_wish_brand(wish_id: int, brand_id: int, session: AsyncSession = Depends(get_session)):
    wish_brand = await session.execute(select(WishBrand).where(
            WishBrand.wish_id == wish_id).where(
                WishBrand.brand_id == brand_id))
    wish_brand = wish_brand.scalars().first()
    if not wish_brand:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='WishBrand not found')
    await session.delete(wish_brand)
    await session.commit()
