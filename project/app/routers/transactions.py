from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Security
from starlette.status import (
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from app.auth import get_auth, confirm_auth_user
from app.db import get_session
from app.models.product import Product
from app.models.transaction import (
    Transaction,
    TransactionCreate,
    TransactionRead,
    TransactionReadFull,
    TransactionUpdate,
)
from app.models.user import User
from app.utils.enums import TransactionStatus
from fastapi_auth0 import Auth0User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


router = APIRouter()


# List
@router.get(
    "/",
    response_model=list[TransactionRead],
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def list_transactions(
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["read:transactions"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["read:transactions"], session
    )  # Confirm permissions
    result = await session.execute(select(Transaction))
    transactions = result.scalars().all()
    return transactions


# Detail
@router.get(
    "/{transaction_id}",
    response_model=TransactionReadFull,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def get_transaction(
    transaction_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    transaction = await session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Transaction not found"
        )
    await confirm_auth_user(
        auth0_user,
        ["read:transactions"],
        session,
        user_id=[transaction.user_id, transaction.product.user_id],
    )  # Confirm permissions
    return transaction


# Insert
@router.post(
    "/",
    response_model=TransactionRead,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def add_transaction(
    new_transaction: TransactionCreate,
    auth0_user: Auth0User = Security(
        get_auth().get_user, scopes=["write:transactions"]
    ),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["write:transactions"], session
    )  # Confirm permissions
    if new_transaction.product_id is not None:
        product = await session.get(Product, new_transaction.product_id)
        if not product:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Product not found"
            )
    if new_transaction.buyer_id is not None:
        user = await session.get(User, new_transaction.buyer_id)
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    if new_transaction.product_id is not None:
        existing_transaction = await session.execute(
            select(Transaction)
            .where(Transaction.product_id == new_transaction.product_id)
            .where(Transaction.status != TransactionStatus.cancelled)
        )
        existing_transaction = existing_transaction.scalars().all()
        if existing_transaction:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="There is already an active transaction for the same product",
            )
    new_transaction = Transaction(**new_transaction.dict())
    session.add(new_transaction)
    await session.commit()
    await session.refresh(new_transaction)
    return new_transaction


# Update
@router.patch(
    "/{transaction_id}",
    response_model=TransactionRead,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    transaction = await session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Transaction not found"
        )
    await confirm_auth_user(
        auth0_user,
        ["modify:transactions"],
        session,
        user_id=[transaction.user_id, transaction.product.user_id],
    )  # Confirm permissions
    update_data = payload.dict(exclude_unset=True)
    if "product_id" in update_data:
        product = await session.get(Product, update_data["product_id"])
        if not product:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Product not found"
            )
    if "buyer_id" in update_data:
        user = await session.get(User, update_data["buyer_id"])
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    if "product_id" in update_data:
        existing_transaction = await session.execute(
            select(Transaction)
            .where(
                Transaction.product_id
                == update_data.get("product_id", transaction.product_id)
            )
            .where(Transaction.status != TransactionStatus.cancelled)
        )
        existing_transaction = existing_transaction.scalars().all()
        if existing_transaction:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="There is already an active transaction for the same product",
            )
    for key, value in update_data.items():
        setattr(transaction, key, value)
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)
    return transaction


# Delete
@router.delete(
    "/{transaction_id}",
    status_code=HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def delete_transaction(
    transaction_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    transaction = await session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Transaction not found"
        )
    await confirm_auth_user(
        auth0_user,
        ["delete:transactions"],
        session,
        user_id=[transaction.user_id, transaction.product.user_id],
    )  # Confirm permissions
    # Soft delete
    update_data = {"deleted_at": datetime.utcnow()}
    for key, value in update_data.items():
        setattr(transaction, key, value)
    session.add(transaction)
    await session.commit()
