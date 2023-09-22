from fastapi import APIRouter, Depends, HTTPException, Security
from starlette.status import (
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from app.auth import get_auth, confirm_auth_user
from app.db import get_session
from app.models.category import (
    Category,
    CategoryCreate,
    CategoryRead,
    CategoryReadFull,
    CategoryUpdate,
)
from fastapi_auth0 import Auth0User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


router = APIRouter()


# List
@router.get(
    "/",
    response_model=list[CategoryRead],
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def list_categories(
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["read:categories"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["read:categories"], session
    )  # Confirm permissions
    result = await session.execute(select(Category))
    categories = result.scalars().all()
    return categories


# Detail
@router.get(
    "/{category_id}",
    response_model=CategoryReadFull,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def get_category(
    category_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["read:categories"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["read:categories"], session
    )  # Confirm permissions
    categ = await session.get(Category, category_id)
    if not categ:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Category not found")
    if categ.parent_id is not None:
        categ.parent = await session.get(Category, categ.parent_id)
    return categ


# Insert
@router.post(
    "/",
    response_model=CategoryReadFull,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def add_category(
    categ: CategoryCreate,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["write:categories"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["write:categories"], session
    )  # Confirm permissions
    if categ.parent_id is not None:
        parent = await session.get(Category, categ.parent_id)
        if not parent:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Parent not found"
            )
    existing_category = await session.execute(
        select(Category)
        .where(Category.name_en == categ.name_en)
        .where(Category.parent_id == categ.parent_id)
    )
    existing_category = existing_category.scalars().all()
    if existing_category:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="The given category already exists"
        )
    category = Category(**categ.dict())
    session.add(category)
    await session.commit()
    await session.refresh(category)
    if category.parent_id is not None:
        category.parent = await session.get(Category, category.parent_id)
    return category


# Update
@router.patch(
    "/{category_id}",
    response_model=CategoryReadFull,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["modify:categories"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["modify:categories"], session
    )  # Confirm permissions
    category = await session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Category not found")
    update_data = payload.dict(exclude_unset=True)
    if "parent_id" in update_data:
        parent = await session.get(Category, update_data["parent_id"])
        if not parent:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Parent not found"
            )
    if "name_en" in update_data or "parent_id" in update_data:
        existing_category = await session.execute(
            select(Category)
            .where(Category.name_en == update_data.get("name_en", category.name_en))
            .where(
                Category.parent_id == update_data.get("parent_id", category.parent_id)
            )
        )
        existing_category = existing_category.scalars().all()
        if existing_category:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="The given category already exists",
            )
    for key, value in update_data.items():
        setattr(category, key, value)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    if category.parent_id is not None:
        category.parent = await session.get(Category, category.parent_id)
    return category


# Delete
@router.delete(
    "/{category_id}",
    status_code=HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def delete_category(
    category_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["delete.categories"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["delete:categories"], session
    )  # Confirm permissions
    category = await session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Category not found")
    await session.delete(category)
    await session.commit()
