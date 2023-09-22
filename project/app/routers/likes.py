from fastapi import APIRouter, Depends, HTTPException, Security
from starlette.status import (
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from app.auth import get_auth, confirm_auth_user
from app.db import get_session
from app.models.like import Like, LikeCreate, LikeRead, LikeUpdate
from app.models.product import Product
from app.models.user import User
from fastapi_auth0 import Auth0User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


router = APIRouter()


# List
@router.get(
    "/",
    response_model=list[LikeRead],
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def list_likes(
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["read:likes"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(auth0_user, ["read:likes"], session)  # Confirm permissions
    result = await session.execute(select(Like))
    likes = result.scalars().all()
    return likes


# Detail
@router.get(
    "/{like_id}",
    response_model=LikeRead,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def get_like(
    like_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["read:likes"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(auth0_user, ["read:likes"], session)  # Confirm permissions
    like = await session.get(Like, like_id)
    if not like:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Like not found")
    return like


# Insert
@router.post(
    "/", response_model=LikeRead, dependencies=[Depends(get_auth().implicit_scheme)]
)
async def add_like(
    new_like: LikeCreate,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["write:likes"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(auth0_user, ["write:likes"], session)  # Confirm permissions
    if new_like.product_id is not None:
        product = await session.get(Product, new_like.product_id)
        if not product:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Product not found"
            )
    if new_like.user_id is not None:
        user = await session.get(User, new_like.user_id)
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    if new_like.product_id is not None and new_like.user_id is not None:
        existing_like = await session.execute(
            select(Like)
            .where(Like.product_id == new_like.product_id)
            .where(Like.user_id == new_like.user_id)
        )
        existing_like = existing_like.scalars().all()
        if existing_like:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="The given like already exists"
            )
    new_like = Like(**new_like.dict())
    session.add(new_like)
    await session.commit()
    await session.refresh(new_like)
    return new_like


# Update
@router.patch(
    "/{like_id}",
    response_model=LikeRead,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def update_like(
    like_id: int,
    payload: LikeUpdate,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["modify:likes"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["modify:likes"], session
    )  # Confirm permissions
    like = await session.get(Like, like_id)
    if not like:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Like not found")
    update_data = payload.dict(exclude_unset=True)
    if "product_id" in update_data:
        product = await session.get(Product, update_data["product_id"])
        if not product:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Product not found"
            )
    if "user_id" in update_data:
        user = await session.get(User, update_data["user_id"])
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    if "product_id" in update_data or "user_id" in update_data:
        existing_like = await session.execute(
            select(Like)
            .where(Like.product_id == update_data.get("product_id", like.product_id))
            .where(Like.user_id == update_data.get("user_id", like.user_id))
        )
        existing_like = existing_like.scalars().all()
        if existing_like:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="The given like already exists"
            )
    for key, value in update_data.items():
        setattr(like, key, value)
    session.add(like)
    await session.commit()
    await session.refresh(like)
    return like


# Delete
@router.delete(
    "/{like_id}",
    status_code=HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def delete_like(
    like_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    like = await session.get(Like, like_id)
    await confirm_auth_user(
        auth0_user, ["delete:likes"], session, user_id=like.user_id
    )  # Confirm permissions
    if not like:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Like not found")
    await session.delete(like)
    await session.commit()
