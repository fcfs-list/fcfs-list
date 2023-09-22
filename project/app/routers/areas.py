from fastapi import APIRouter, Depends, HTTPException, Security
from starlette.status import (
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from app.auth import get_auth, confirm_auth_user
from app.db import get_session
from app.models.area import Area, AreaCreate, AreaRead, AreaReadFull, AreaUpdate
from app.models.user import User
from fastapi_auth0 import Auth0User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


router = APIRouter()


# List
@router.get(
    "/",
    response_model=list[AreaRead],
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def list_areas(
    _: Auth0User = Security(get_auth().get_user, scopes=["read:areas"]),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Area))
    areas = result.scalars().unique().all()
    return areas


# Detail
@router.get(
    "/{area_id}",
    response_model=AreaReadFull,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def get_area(
    area_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["read:areas"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(auth0_user, ["read:areas"], session)  # Confirm permissions
    area = await session.get(Area, area_id)
    if not area:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Area not found")
    if area.parent_id is not None:
        area.parent = await session.get(Area, area.parent_id)
    return area


# Insert
@router.post(
    "/", response_model=AreaReadFull, dependencies=[Depends(get_auth().implicit_scheme)]
)
async def add_area(
    area: AreaCreate,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["write:areas"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(auth0_user, ["write:areas"], session)  # Confirm permissions
    if area.parent_id is not None:
        parent = await session.get(Area, area.parent_id)
        if not parent:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Parent not found"
            )
    if area.created_by is not None:
        created_by = await session.get(User, area.created_by)
        if not created_by:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="User (created by) not found"
            )
    existing_area = await session.execute(
        select(Area)
        .where(Area.name_en == area.name_en)
        .where(Area.parent_id == area.parent_id)
    )
    existing_area = existing_area.scalars().all()
    if existing_area:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="The given area already exists"
        )
    area = Area(**area.dict())
    session.add(area)
    await session.commit()
    await session.refresh(area)
    if area.parent_id is not None:
        area.parent = await session.get(Area, area.parent_id)
    return area


# Update
@router.patch(
    "/{area_id}",
    response_model=AreaReadFull,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def update_area(
    area_id: int,
    payload: AreaUpdate,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    area = await session.get(Area, area_id)
    await confirm_auth_user(
        auth0_user, ["modify:areas"], session, user_id=area.author
    )  # Confirm permissions
    if not area:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Area not found")
    update_data = payload.dict(exclude_unset=True)
    if "parent_id" in update_data:
        parent = await session.get(Area, update_data["parent_id"])
        if not parent:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Parent not found"
            )
    if "created_id" in update_data:
        created_by = await session.get(User, update_data["parent_id"])
        if not created_by:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="User (created by) not found"
            )
    if "name_en" in update_data or "parent_id" in update_data:
        existing_area = await session.execute(
            select(Area)
            .where(Area.name_en == update_data.get("name_en", area.name_en))
            .where(Area.parent_id == update_data.get("parent_id", area.parent_id))
        )
        existing_area = existing_area.scalars().all()
        if existing_area:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="The given area already exists"
            )
    for key, value in update_data.items():
        setattr(area, key, value)
    session.add(area)
    await session.commit()
    await session.refresh(area)
    if area.parent_id is not None:
        area.parent = await session.get(Area, area.parent_id)
    return area


# Delete
@router.delete(
    "/{area_id}",
    status_code=HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def delete_area(
    area_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    area = await session.get(Area, area_id)
    await confirm_auth_user(
        auth0_user, ["delete:areas"], session, user_id=area.author
    )  # Confirm permissions
    if not area:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Area not found")
    await session.delete(area)
    await session.commit()
