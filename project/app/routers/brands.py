from fastapi import APIRouter, Depends, HTTPException, Security
from starlette.status import (
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from app.auth import get_auth, confirm_auth_user
from app.db import get_session
from app.models.brand import Brand, BrandCreate, BrandRead, BrandUpdate
from fastapi_auth0 import Auth0User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


router = APIRouter()


# List
@router.get(
    "/",
    response_model=list[BrandRead],
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def list_brands(
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["read:brands"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(auth0_user, ["read:brands"], session)  # Confirm permissions
    result = await session.execute(select(Brand))
    brands = result.scalars().all()
    return brands


# Detail
@router.get(
    "/{brand_id}",
    response_model=BrandRead,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def get_brand(
    brand_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["read:brands"]),
    session: AsyncSession = Depends(get_session),
):
    brand = await session.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Brand not found")
    return brand


# Insert
@router.post(
    "/", response_model=BrandRead, dependencies=[Depends(get_auth().implicit_scheme)]
)
async def add_brand(
    brand: BrandCreate,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["write:brands"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["write:brands"], session
    )  # Confirm permissions
    existing_brand = await session.execute(
        select(Brand)
        .where(Brand.name_en == brand.name_en)
        .where(Brand.name_ja == brand.name_ja)
    )
    existing_brand = existing_brand.scalars().all()
    if existing_brand:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="The given brand already exists"
        )
    brand = Brand(**brand.dict())
    session.add(brand)
    await session.commit()
    await session.refresh(brand)
    return brand


# Update
@router.patch(
    "/{brand_id}",
    response_model=BrandRead,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def update_brand(
    brand_id: int,
    payload: BrandUpdate,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["modify:brands"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["modify:brands"], session
    )  # Confirm permissions
    brand = await session.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Brand not found")
    update_data = payload.dict(exclude_unset=True)
    if "name_en" in update_data or "name_ja" in update_data:
        existing_brand = await session.execute(
            select(Brand)
            .where(Brand.name_en == update_data.get("name_en", brand.name_en))
            .where(Brand.name_ja == update_data.get("name_ja", brand.name_ja))
        )
        existing_brand = existing_brand.scalars().all()
        if existing_brand:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="The given brand already exists",
            )
    for key, value in update_data.items():
        setattr(brand, key, value)
    session.add(brand)
    await session.commit()
    await session.refresh(brand)
    return brand


# Delete
@router.delete(
    "/{brand_id}",
    status_code=HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def delete_brand(
    brand_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["delete:brands"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["delete:brands"], session
    )  # Confirm permissions
    brand = await session.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Brand not found")
    await session.delete(brand)
    await session.commit()
