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
from app.models.user import User
from app.models.wish import Wish, WishCreate, WishRead, WishReadFull, WishUpdate
from app.models.wish_area import WishArea
from app.models.wish_brand import WishBrand
from app.models.wish_category import WishCategory
from fastapi_auth0 import Auth0User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


router = APIRouter()


# List
@router.get(
    "/",
    response_model=list[WishRead],
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def list_wishes(
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["read:wishes"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(auth0_user, ["read:wishes"], session)  # Confirm permissions
    result = await session.execute(select(Wish))
    wishes = result.scalars().unique().all()
    return wishes


# Detail
@router.get(
    "/{wish_id}",
    response_model=WishReadFull,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def get_wish(
    wish_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    wish = await session.get(Wish, wish_id)
    if not wish:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Wish not found")
    await confirm_auth_user(
        auth0_user, ["read:wishes"], session, user_id=wish.user_id
    )  # Confirm permissions
    return wish


# Insert
@router.post(
    "/", response_model=WishRead, dependencies=[Depends(get_auth().implicit_scheme)]
)
async def add_wish(
    new_wish: WishCreate,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["write:wishes"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["write:wishes"], session
    )  # Confirm permissions
    if new_wish.user_id is not None:
        user = await session.get(User, new_wish.user_id)
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    new_wish = Wish(
        user_id=new_wish.user_id, keywords=new_wish.keywords, details=new_wish.details
    )
    session.add(new_wish)
    await session.commit()
    await session.refresh(new_wish)
    return new_wish


# Update
@router.patch(
    "/{wish_id}",
    response_model=WishRead,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def update_wish(
    wish_id: int,
    payload: WishUpdate,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    wish = await session.get(Wish, wish_id)
    if not wish:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Wish not found")
    await confirm_auth_user(
        auth0_user, ["modify:wishes"], session, user_id=wish.user_id
    )  # Confirm permissions
    update_data = payload.dict(exclude_unset=True)
    if "user_id" in update_data:
        user = await session.get(User, update_data["user_id"])
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    for key, value in update_data.items():
        setattr(wish, key, value)
    session.add(wish)
    await session.commit()
    await session.refresh(wish)
    return wish


# Delete
@router.delete(
    "/{wish_id}",
    status_code=HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def delete_wish(
    wish_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    wish = await session.get(Wish, wish_id)
    if not wish:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Wish not found")
    await confirm_auth_user(
        auth0_user, ["delete:wishes"], session, user_id=wish.user_id
    )  # Confirm permissions
    await session.delete(wish)
    await session.commit()


## Wish Areas ##


# Insert
@router.post(
    "/{wish_id}/areas/{area_id}",
    response_model=WishReadFull,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def add_wish_area(
    wish_id: int,
    area_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    wish = await session.get(Wish, wish_id)
    if not wish:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Wish not found")
    await confirm_auth_user(
        auth0_user, ["modify:wishes"], session, user_id=wish.user_id
    )  # Confirm permissions
    area = await session.get(Area, area_id)
    if not area:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Area not found")
    wish_area = await session.execute(
        select(WishArea)
        .where(WishArea.wish_id == wish_id)
        .where(WishArea.area_id == area_id)
    )
    wish_area = wish_area.scalars().all()
    if wish_area:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="WishArea already exists"
        )
    wish_area = WishArea(area_id=area_id, wish_id=wish_id)
    session.add(wish_area)
    await session.commit()
    await session.refresh(wish)
    return wish


# Delete
@router.delete(
    "/{wish_id}/areas/{area_id}",
    status_code=HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def delete_wish_area(
    wish_id: int,
    area_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    wish_area = await session.execute(
        select(WishArea)
        .where(WishArea.wish_id == wish_id)
        .where(WishArea.area_id == area_id)
    )
    wish_area = wish_area.scalars().first()
    if not wish_area:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="WishArea not found")
    await confirm_auth_user(
        auth0_user, ["modify:wishes"], session, user_id=wish_area.wish.user_id
    )  # Confirm permissions
    await session.delete(wish_area)
    await session.commit()


## Wish Categories ##


# Insert
@router.post(
    "/{wish_id}/categories/{category_id}",
    response_model=WishReadFull,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def add_wish_category(
    wish_id: int,
    category_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    wish = await session.get(Wish, wish_id)
    if not wish:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Wish not found")
    await confirm_auth_user(
        auth0_user, ["modify:wishes"], session, user_id=wish.user_id
    )  # Confirm permissions
    category = await session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Category not found")
    wish_category = await session.execute(
        select(WishCategory)
        .where(WishCategory.wish_id == wish_id)
        .where(WishCategory.category_id == category_id)
    )
    wish_category = wish_category.scalars().all()
    if wish_category:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="WishCategory already exists"
        )
    wish_category = WishCategory(category_id=category_id, wish_id=wish_id)
    session.add(wish_category)
    await session.commit()
    await session.refresh(wish)
    return wish


# Delete
@router.delete(
    "/{wish_id}/categories/{category_id}",
    status_code=HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def delete_wish_category(
    wish_id: int,
    category_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    wish_category = await session.execute(
        select(WishCategory)
        .where(WishCategory.wish_id == wish_id)
        .where(WishCategory.category_id == category_id)
    )
    wish_category = wish_category.scalars().first()
    if not wish_category:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="WishCategory not found"
        )
    await confirm_auth_user(
        auth0_user, ["modify:wishes"], session, user_id=wish_category.wish.user_id
    )  # Confirm permissions
    await session.delete(wish_category)
    await session.commit()


## Wish Brands ##


# Insert
@router.post(
    "/{wish_id}/brands/{brand_id}",
    response_model=WishReadFull,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def add_wish_brand(
    wish_id: int,
    brand_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["modify:wishes"]),
    session: AsyncSession = Depends(get_session),
):
    wish = await session.get(Wish, wish_id)
    if not wish:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Wish not found")
    brand = await session.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Brand not found")
    wish_brand = await session.execute(
        select(WishBrand)
        .where(WishBrand.wish_id == wish_id)
        .where(WishBrand.brand_id == brand_id)
    )
    wish_brand = wish_brand.scalars().all()
    if wish_brand:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="WishBrand already exists"
        )
    wish_brand = WishBrand(brand_id=brand_id, wish_id=wish_id)
    session.add(wish_brand)
    await session.commit()
    await session.refresh(wish)
    return wish


# Delete
@router.delete(
    "/{wish_id}/brands/{brand_id}",
    status_code=HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def delete_wish_brand(
    wish_id: int,
    brand_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["modify:wishes"]),
    session: AsyncSession = Depends(get_session),
):
    wish_brand = await session.execute(
        select(WishBrand)
        .where(WishBrand.wish_id == wish_id)
        .where(WishBrand.brand_id == brand_id)
    )
    wish_brand = wish_brand.scalars().first()
    if not wish_brand:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="WishBrand not found"
        )
    await session.delete(wish_brand)
    await session.commit()
