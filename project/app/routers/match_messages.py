from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND

from app.db import get_session
from app.models.match_message import MatchMessage, MatchMessageCreate, MatchMessageUpdate, MatchMessageRead
from app.models.match import Match
from app.models.user import User

router = APIRouter()

# List
@router.get('/', response_model=list[MatchMessageRead])
async def list_match_messages(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(MatchMessage))
    match_messages = result.scalars().all()
    return match_messages

# Detail
@router.get('/{match_message_id}', response_model=MatchMessageRead)
async def get_match_message(match_message_id: int, session: AsyncSession = Depends(get_session)):
    match_message = await session.get(MatchMessage, match_message_id)
    if not match_message:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='MatchMessage not found')
    return match_message

# Insert
@router.post('/', response_model=MatchMessageRead)
async def add_match_message(new_match_message: MatchMessageCreate, session: AsyncSession = Depends(get_session)):
    if new_match_message.match_id is not None:
        match = await session.get(Match, new_match_message.match_id)
        if not match:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Match not found')
    if new_match_message.user_id is not None:
        user = await session.get(User, new_match_message.user_id)
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User not found')
    new_match_message = MatchMessage(**new_match_message.dict())
    session.add(new_match_message)
    await session.commit()
    await session.refresh(new_match_message)
    return new_match_message

# Update
@router.patch('/{match_message_id}', response_model=MatchMessageRead)
async def update_match_message(match_message_id: int, payload: MatchMessageUpdate, session: AsyncSession = Depends(get_session)):
    match_message = await session.get(MatchMessage, match_message_id)
    if not match_message:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='MatchMessage not found')
    update_data = payload.dict(exclude_unset=True)
    if 'match_id' in update_data:
        match = await session.get(Match, update_data['match_id'])
        if not match:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Match not found')
    if 'user_id' in update_data:
        user = await session.get(User, update_data['user_id'])
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User not found')
    for key, value in update_data.items():
        setattr(match_message, key, value)
    session.add(match_message)
    await session.commit()
    await session.refresh(match_message)
    return match_message


# Delete
@router.delete('/{match_message_id}', status_code=HTTP_204_NO_CONTENT)
async def delete_match_message(match_message_id: int, session: AsyncSession = Depends(get_session)):
    match_message = await session.get(MatchMessage, match_message_id)
    if not match_message:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='MatchMessage not found')
    await session.delete(match_message)
    await session.commit()
