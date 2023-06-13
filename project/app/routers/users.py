from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from app.db import get_session
from app.models.user import User, UserCreate, UserUpdate, UserRead, UserReadFull
from app.models.area import Area
from app.models.user_area import UserArea

router = APIRouter()

# List
@router.get('/', response_model=list[UserRead])
async def list_users(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User))
    users = result.scalars().unique().all()
    return users

# Detail
@router.get('/{user_id}', response_model=UserReadFull)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User not found')
    return user

# Insert
@router.post('/', response_model=UserReadFull)
async def add_user(user: UserCreate, session: AsyncSession = Depends(get_session)):
    user = User(**user.dict())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

# Update
@router.patch('/{user_id}', response_model=UserReadFull)
async def update_user(user_id: int, payload: UserUpdate, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User not found')
    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


# Delete
@router.delete('/{user_id}', status_code=HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User not found')
    await session.delete(user)
    await session.commit()


## User Areas ##

# Insert
@router.post('/{user_id}/areas/{area_id}', response_model=UserReadFull)
async def add_user_area(user_id: int, area_id: int, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User not found')
    area = await session.get(Area, area_id)
    if not area:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Area not found')
    user_area = await session.execute(select(UserArea).where(
            UserArea.user_id == user_id).where(
                UserArea.area_id == area_id))
    user_area = user_area.scalars().all()
    if user_area:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='UserArea already exists')
    user_area = UserArea(
        area_id=area_id,
        user_id=user_id
    )
    session.add(user_area)
    await session.commit()
    await session.refresh(user)
    return user

# Delete
@router.delete('/{user_id}/areas/{area_id}', status_code=HTTP_204_NO_CONTENT)
async def delete_user_area(user_id: int, area_id: int, session: AsyncSession = Depends(get_session)):
    user_area = await session.execute(select(UserArea).where(
            UserArea.user_id == user_id).where(
                UserArea.area_id == area_id))
    user_area = user_area.scalars().first()
    if not user_area:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='UserArea not found')
    await session.delete(user_area)
    await session.commit()
