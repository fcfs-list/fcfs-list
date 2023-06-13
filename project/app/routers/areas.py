from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from app.db import get_session
from app.models.area import Area, AreaCreate, AreaUpdate, AreaRead, AreaReadFull
from app.models.user import User

router = APIRouter()

# List
@router.get('/', response_model=list[AreaRead])
async def list_areas(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Area))
    areas = result.scalars().unique().all()
    return areas

# Detail
@router.get('/{area_id}', response_model=AreaReadFull)
async def get_area(area_id: int, session: AsyncSession = Depends(get_session)):
    area = await session.get(Area, area_id)
    if not area:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Area not found')
    if area.parent_id is not None:
        area.parent = await session.get(Area, area.parent_id)
    return area

# Insert
@router.post('/', response_model=AreaReadFull)
async def add_area(area: AreaCreate, session: AsyncSession = Depends(get_session)):
    if area.parent_id is not None:
        parent = await session.get(Area, area.parent_id)
        if not parent:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Parent not found')
    if area.created_by is not None:
        created_by = await session.get(User, area.created_by)
        if not created_by:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User (created by) not found')
    existing_area = await session.execute(select(Area).where(
        Area.name_en == area.name_en).where(Area.parent_id == area.parent_id))
    existing_area = existing_area.scalars().all()
    if existing_area:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='The given area already exists')
    area = Area(**area.dict())
    session.add(area)
    await session.commit()
    await session.refresh(area)
    if area.parent_id is not None:
        area.parent = await session.get(Area, area.parent_id)
    return area

# Update
@router.patch('/{area_id}', response_model=AreaReadFull)
async def update_area(area_id: int, payload: AreaUpdate, session: AsyncSession = Depends(get_session)):
    area = await session.get(Area, area_id)
    if not area:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Area not found')
    update_data = payload.dict(exclude_unset=True)
    if 'parent_id' in update_data:
        parent = await session.get(Area, update_data['parent_id'])
        if not parent:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Parent not found')
    if 'created_id' in update_data:
        created_by = await session.get(User, update_data['parent_id'])
        if not created_by:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User (created by) not found')
    if 'name_en' in update_data or 'parent_id' in update_data:
        existing_area = await session.execute(select(Area).where(
            Area.name_en == update_data.get('name_en', area.name_en)).where(
                Area.parent_id == update_data.get('parent_id', area.parent_id)))
        existing_area = existing_area.scalars().all()
        if existing_area:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='The given area already exists')
    for key, value in update_data.items():
        setattr(area, key, value)
    session.add(area)
    await session.commit()
    await session.refresh(area)
    if area.parent_id is not None:
        area.parent = await session.get(Area, area.parent_id)
    return area


# Delete
@router.delete('/{area_id}', status_code=HTTP_204_NO_CONTENT)
async def delete_area(area_id: int, session: AsyncSession = Depends(get_session)):
    area = await session.get(Area, area_id)
    if not area:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Area not found')
    await session.delete(area)
    await session.commit()
