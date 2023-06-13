from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND

from app.db import get_session
from app.models.transaction_message import TransactionMessage, TransactionMessageCreate, TransactionMessageUpdate, TransactionMessageRead
from app.models.transaction import Transaction
from app.models.user import User

router = APIRouter()

# List
@router.get('/', response_model=list[TransactionMessageRead])
async def list_transaction_messages(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(TransactionMessage))
    transaction_messages = result.scalars().all()
    return transaction_messages

# Detail
@router.get('/{transaction_message_id}', response_model=TransactionMessageRead)
async def get_transaction_message(transaction_message_id: int, session: AsyncSession = Depends(get_session)):
    transaction_message = await session.get(TransactionMessage, transaction_message_id)
    if not transaction_message:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='TransactionMessage not found')
    return transaction_message

# Insert
@router.post('/', response_model=TransactionMessageRead)
async def add_transaction_message(new_transaction_message: TransactionMessageCreate, session: AsyncSession = Depends(get_session)):
    if new_transaction_message.transaction_id is not None:
        transaction = await session.get(Transaction, new_transaction_message.transaction_id)
        if not transaction:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Transaction not found')
    if new_transaction_message.user_id is not None:
        user = await session.get(User, new_transaction_message.user_id)
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User not found')
    new_transaction_message = TransactionMessage(**new_transaction_message.dict())
    session.add(new_transaction_message)
    await session.commit()
    await session.refresh(new_transaction_message)
    return new_transaction_message

# Update
@router.patch('/{transaction_message_id}', response_model=TransactionMessageRead)
async def update_transaction_message(transaction_message_id: int, payload: TransactionMessageUpdate, session: AsyncSession = Depends(get_session)):
    transaction_message = await session.get(TransactionMessage, transaction_message_id)
    if not transaction_message:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='TransactionMessage not found')
    update_data = payload.dict(exclude_unset=True)
    if 'transaction_id' in update_data:
        transaction = await session.get(Transaction, update_data['transaction_id'])
        if not transaction:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Transaction not found')
    if 'user_id' in update_data:
        user = await session.get(User, update_data['user_id'])
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User not found')
    for key, value in update_data.items():
        setattr(transaction_message, key, value)
    session.add(transaction_message)
    await session.commit()
    await session.refresh(transaction_message)
    return transaction_message


# Delete
@router.delete('/{transaction_message_id}', status_code=HTTP_204_NO_CONTENT)
async def delete_transaction_message(transaction_message_id: int, session: AsyncSession = Depends(get_session)):
    transaction_message = await session.get(TransactionMessage, transaction_message_id)
    if not transaction_message:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='TransactionMessage not found')
    await session.delete(transaction_message)
    await session.commit()
