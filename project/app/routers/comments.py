from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND

from app.db import get_session
from app.models.comment import Comment, CommentCreate, CommentUpdate, CommentRead
from app.models.product import Product
from app.models.user import User

router = APIRouter()

# List
@router.get('/', response_model=list[CommentRead])
async def list_comments(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Comment))
    comments = result.scalars().all()
    return comments

# Detail
@router.get('/{comment_id}', response_model=CommentRead)
async def get_comment(comment_id: int, session: AsyncSession = Depends(get_session)):
    comment = await session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Comment not found')
    return comment

# Insert
@router.post('/', response_model=CommentRead)
async def add_comment(new_comment: CommentCreate, session: AsyncSession = Depends(get_session)):
    if new_comment.product_id is not None:
        product = await session.get(Product, new_comment.product_id)
        if not product:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Product not found')
    if new_comment.user_id is not None:
        user = await session.get(User, new_comment.user_id)
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User not found')
    new_comment = Comment(**new_comment.dict())
    session.add(new_comment)
    await session.commit()
    await session.refresh(new_comment)
    return new_comment

# Update
@router.patch('/{comment_id}', response_model=CommentRead)
async def update_comment(comment_id: int, payload: CommentUpdate, session: AsyncSession = Depends(get_session)):
    comment = await session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Comment not found')
    update_data = payload.dict(exclude_unset=True)
    if 'product_id' in update_data:
        product = await session.get(Product, update_data['product_id'])
        if not product:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Product not found')
    if 'user_id' in update_data:
        user = await session.get(User, update_data['user_id'])
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User not found')
    for key, value in update_data.items():
        setattr(comment, key, value)
    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    return comment


# Delete
@router.delete('/{comment_id}', status_code=HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: int, session: AsyncSession = Depends(get_session)):
    comment = await session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Comment not found')
    await session.delete(comment)
    await session.commit()
