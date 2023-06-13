from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from app.db import get_session
from app.models.category import Category, CategoryCreate, CategoryUpdate, CategoryRead, CategoryReadFull

router = APIRouter()

# List
@router.get('/', response_model=list[CategoryRead])
async def list_categories(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Category))
    categories = result.scalars().all()
    return categories

# Detail
@router.get('/{category_id}', response_model=CategoryReadFull)
async def get_category(category_id: int, session: AsyncSession = Depends(get_session)):
    categ = await session.get(Category, category_id)
    if not categ:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Category not found')
    if categ.parent_id is not None:
        categ.parent = await session.get(Category, categ.parent_id)
    return categ

# Insert
@router.post('/', response_model=CategoryReadFull)
async def add_category(categ: CategoryCreate, session: AsyncSession = Depends(get_session)):
    if categ.parent_id is not None:
        parent = await session.get(Category, categ.parent_id)
        if not parent:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Parent not found')
    existing_category = await session.execute(select(Category).where(
        Category.name_en == categ.name_en).where(
                Category.parent_id == categ.parent_id))
    existing_category = existing_category.scalars().all()
    if existing_category:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='The given category already exists')
    category = Category(**categ.dict())
    session.add(category)
    await session.commit()
    await session.refresh(category)
    if category.parent_id is not None:
        category.parent = await session.get(Category, category.parent_id)
    return category

# Update
@router.patch('/{category_id}', response_model=CategoryReadFull)
async def update_category(category_id: int, payload: CategoryUpdate, session: AsyncSession = Depends(get_session)):
    category = await session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Category not found')
    update_data = payload.dict(exclude_unset=True)
    if 'parent_id' in update_data:
        parent = await session.get(Category, update_data['parent_id'])
        if not parent:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Parent not found')
    if 'name_en' in update_data or 'parent_id' in update_data:
        existing_category = await session.execute(select(Category).where(
            Category.name_en == update_data.get('name_en', category.name_en)).where(
                Category.parent_id == update_data.get('parent_id', category.parent_id)))
        existing_category = existing_category.scalars().all()
        if existing_category:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='The given category already exists')
    for key, value in update_data.items():
        setattr(category, key, value)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    if category.parent_id is not None:
        category.parent = await session.get(Category, category.parent_id)
    return category


# Delete
@router.delete('/{category_id}', status_code=HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, session: AsyncSession = Depends(get_session)):
    category = await session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Category not found')
    await session.delete(category)
    await session.commit()
