import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Security
from starlette.status import (
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)

from app.auth import get_auth, confirm_auth_user
from app.db import get_session
from app.models.area import Area
from app.models.user import User, UserCreate, UserRead, UserReadFull, UserUpdate
from app.models.user_area import UserArea
from fastapi_auth0 import Auth0User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


router = APIRouter()


# List
@router.get(
    "/",
    response_model=list[UserRead],
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def list_users(
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["read:users"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(auth0_user, ["read:users"], session)  # Confirm permissions
    result = await session.execute(select(User))
    users = result.scalars().unique().all()
    return users


# Detail
@router.get(
    "/{user_id}",
    response_model=UserReadFull,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def get_user(
    user_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["read:users"], session, user_id=user_id
    )  # Confirm permissions
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    return user


# Insert
@router.post(
    "/", response_model=UserReadFull, dependencies=[Depends(get_auth().implicit_scheme)]
)
async def add_user(
    user: UserCreate,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["write:users"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(auth0_user, ["write:users"], session)  # Confirm permissions
    user = User(**user.dict())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


# Sign up
@router.post(
    "/signup",
    response_model=UserReadFull,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def sign_up(
    user: UserCreate,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    user = User(**user.dict())
    user.auth0_id = auth0_user.id
    user.email = auth0_user.email
    user.name = "%s%s" % (auth0_user.email.split("@")[0], random.randint(1000, 9999))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


# Update
@router.patch(
    "/{user_id}",
    response_model=UserReadFull,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["modify:users"], session, user_id=user_id
    )  # Confirm permissions
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


# Delete
@router.delete(
    "/{user_id}",
    status_code=HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def delete_user(
    user_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["delete:users"], session, user_id=user_id
    )  # Confirm permissions
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    # Soft delete
    update_data = {
        "name": "Deleted User",
        "email": f"deleted-{user.email}",
        "phone": None,
        "deleted_at": datetime.utcnow(),
    }
    for key, value in update_data.items():
        setattr(user, key, value)
    session.add(user)
    await session.commit()


## User Areas ##


# Insert
@router.post(
    "/{user_id}/areas/{area_id}",
    response_model=UserReadFull,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def add_user_area(
    user_id: int,
    area_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["modify:users"], session, user_id=user_id
    )  # Confirm permissions
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    area = await session.get(Area, area_id)
    if not area:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Area not found")
    user_area = await session.execute(
        select(UserArea)
        .where(UserArea.user_id == user_id)
        .where(UserArea.area_id == area_id)
    )
    user_area = user_area.scalars().all()
    if user_area:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="UserArea already exists"
        )
    user_area = UserArea(area_id=area_id, user_id=user_id)
    session.add(user_area)
    await session.commit()
    await session.refresh(user)
    return user


# Delete
@router.delete(
    "/{user_id}/areas/{area_id}",
    status_code=HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def delete_user_area(
    user_id: int,
    area_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["modify:users"], session, user_id=user_id
    )  # Confirm permissions
    user_area = await session.execute(
        select(UserArea)
        .where(UserArea.user_id == user_id)
        .where(UserArea.area_id == area_id)
    )
    user_area = user_area.scalars().first()
    if not user_area:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="UserArea not found")
    await session.delete(user_area)
    await session.commit()
