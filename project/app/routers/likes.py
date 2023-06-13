from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from app.db import get_session
from app.models.like import Like, LikeCreate, LikeUpdate, LikeRead
from app.models.product import Product
from app.models.user import User

router = APIRouter()

# List
@router.get('/', response_model=list[LikeRead])
async def list_likes(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Like))
    likes = result.scalars().all()
    return likes

# Detail
@router.get('/{like_id}', response_model=LikeRead)
async def get_like(like_id: int, session: AsyncSession = Depends(get_session)):
    like = await session.get(Like, like_id)
    if not like:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Like not found')
    return like

# Insert
@router.post('/', response_model=LikeRead)
async def add_like(new_like: LikeCreate, session: AsyncSession = Depends(get_session)):
    if new_like.product_id is not None:
        product = await session.get(Product, new_like.product_id)
        if not product:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Product not found')
    if new_like.user_id is not None:
        user = await session.get(User, new_like.user_id)
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User not found')
    if new_like.product_id is not None and new_like.user_id is not None:
        existing_like = await session.execute(select(Like).where(Like.product_id == new_like.product_id).where(Like.user_id == new_like.user_id))
        existing_like = existing_like.scalars().all()
        if existing_like:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='The given like already exists')
    new_like = Like(**new_like.dict())
    session.add(new_like)
    await session.commit()
    await session.refresh(new_like)
    return new_like

# Update
@router.patch('/{like_id}', response_model=LikeRead)
async def update_like(like_id: int, payload: LikeUpdate, session: AsyncSession = Depends(get_session)):
    like = await session.get(Like, like_id)
    if not like:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Like not found')
    update_data = payload.dict(exclude_unset=True)
    if 'product_id' in update_data:
        product = await session.get(Product, update_data['product_id'])
        if not product:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Product not found')
    if 'user_id' in update_data:
        user = await session.get(User, update_data['user_id'])
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User not found')
    if 'product_id' in update_data or 'user_id' in update_data:
        existing_like = await session.execute(select(Like).where(
            Like.product_id == update_data.get('product_id', like.product_id)).where(
                Like.user_id == update_data.get('user_id', like.user_id)))
        existing_like = existing_like.scalars().all()
        if existing_like:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='The given like already exists')
    for key, value in update_data.items():
        setattr(like, key, value)
    session.add(like)
    await session.commit()
    await session.refresh(like)
    return like


# Delete
@router.delete('/{like_id}', status_code=HTTP_204_NO_CONTENT)
async def delete_like(like_id: int, session: AsyncSession = Depends(get_session)):
    like = await session.get(Like, like_id)
    if not like:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Like not found')
    await session.delete(like)
    await session.commit()
