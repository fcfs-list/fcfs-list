from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST

from app.db import get_session
from app.models.transaction import Transaction, TransactionCreate, TransactionUpdate, TransactionRead, TransactionReadFull
from app.models.product import Product
from app.models.user import User
from app.utils.enums import TransactionStatus

router = APIRouter()

# List
@router.get('/', response_model=list[TransactionRead])
async def list_transactions(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Transaction))
    transactions = result.scalars().all()
    return transactions

# Detail
@router.get('/{transaction_id}', response_model=TransactionReadFull)
async def get_transaction(transaction_id: int, session: AsyncSession = Depends(get_session)):
    transaction = await session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Transaction not found')
    return transaction

# Insert
@router.post('/', response_model=TransactionRead)
async def add_transaction(new_transaction: TransactionCreate, session: AsyncSession = Depends(get_session)):
    if new_transaction.product_id is not None:
        product = await session.get(Product, new_transaction.product_id)
        if not product:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Product not found')
    if new_transaction.buyer_id is not None:
        user = await session.get(User, new_transaction.buyer_id)
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User not found')
    if new_transaction.product_id is not None:
        existing_transaction = await session.execute(select(Transaction).where(
            Transaction.product_id == new_transaction.product_id).where(
            Transaction.status != TransactionStatus.cancelled))
        existing_transaction = existing_transaction.scalars().all()
        if existing_transaction:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='There is already an active transaction for the same product'
            )
    new_transaction = Transaction(**new_transaction.dict())
    session.add(new_transaction)
    await session.commit()
    await session.refresh(new_transaction)
    return new_transaction

# Update
@router.patch('/{transaction_id}', response_model=TransactionRead)
async def update_transaction(transaction_id: int, payload: TransactionUpdate, session: AsyncSession = Depends(get_session)):
    transaction = await session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Transaction not found')
    update_data = payload.dict(exclude_unset=True)
    if 'product_id' in update_data:
        product = await session.get(Product, update_data['product_id'])
        if not product:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Product not found')
    if 'buyer_id' in update_data:
        user = await session.get(User, update_data['buyer_id'])
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User not found')
    if 'product_id' in update_data:
        existing_transaction = await session.execute(select(Transaction).where(
            Transaction.product_id == update_data.get('product_id', transaction.product_id)).where(
            Transaction.status != TransactionStatus.cancelled))
        existing_transaction = existing_transaction.scalars().all()
        if existing_transaction:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='There is already an active transaction for the same product'
            )
    for key, value in update_data.items():
        setattr(transaction, key, value)
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)
    return transaction


# Delete
@router.delete('/{transaction_id}', status_code=HTTP_204_NO_CONTENT)
async def delete_transaction(transaction_id: int, session: AsyncSession = Depends(get_session)):
    transaction = await session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Transaction not found')
    await session.delete(transaction)
    await session.commit()
