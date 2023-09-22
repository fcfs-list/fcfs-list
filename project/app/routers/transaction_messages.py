from fastapi import APIRouter, Depends, HTTPException, Security
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND

from app.auth import get_auth, confirm_auth_user
from app.db import get_session
from app.models.transaction import Transaction
from app.models.transaction_message import (
    TransactionMessage,
    TransactionMessageCreate,
    TransactionMessageRead,
    TransactionMessageUpdate,
)
from app.models.user import User
from fastapi_auth0 import Auth0User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


router = APIRouter()


# List
@router.get(
    "/",
    response_model=list[TransactionMessageRead],
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def list_transaction_messages(
    auth0_user: Auth0User = Security(
        get_auth().get_user, scopes=["read:transaction_messages"]
    ),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["read:transaction_messages"], session
    )  # Confirm permissions
    result = await session.execute(select(TransactionMessage))
    transaction_messages = result.scalars().all()
    return transaction_messages


# Detail
@router.get(
    "/{transaction_message_id}",
    response_model=TransactionMessageRead,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def get_transaction_message(
    transaction_message_id: int,
    auth0_user: Auth0User = Security(
        get_auth().get_user, scopes=["read:transaction_messages"]
    ),
    session: AsyncSession = Depends(get_session),
):
    transaction_message = await session.get(TransactionMessage, transaction_message_id)
    if not transaction_message:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="TransactionMessage not found"
        )
    await confirm_auth_user(
        auth0_user,
        ["read:transaction_messages"],
        session,
        user_id=[
            transaction_message.transaction.user_id,
            transaction_message.transaction.product.user_id,
        ],
    )  # Confirm permissions
    return transaction_message


# Insert
@router.post(
    "/",
    response_model=TransactionMessageRead,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def add_transaction_message(
    new_transaction_message: TransactionMessageCreate,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    if new_transaction_message.transaction_id is not None:
        transaction = await session.get(
            Transaction, new_transaction_message.transaction_id
        )
        if not transaction:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Transaction not found"
            )
    if new_transaction_message.user_id is not None:
        user = await session.get(User, new_transaction_message.user_id)
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    await confirm_auth_user(
        auth0_user,
        ["write:transaction_messages"],
        session,
        user_id=[
            new_transaction_message.transaction.user_id,
            new_transaction_message.transaction.product.user_id,
        ],
    )  # Confirm permissions
    new_transaction_message = TransactionMessage(**new_transaction_message.dict())
    session.add(new_transaction_message)
    await session.commit()
    await session.refresh(new_transaction_message)
    return new_transaction_message


# Update
@router.patch(
    "/{transaction_message_id}",
    response_model=TransactionMessageRead,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def update_transaction_message(
    transaction_message_id: int,
    payload: TransactionMessageUpdate,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    transaction_message = await session.get(TransactionMessage, transaction_message_id)
    if not transaction_message:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="TransactionMessage not found"
        )
    await confirm_auth_user(
        auth0_user,
        ["modify:transaction_messages"],
        session,
        user_id=transaction_message.user_id,
    )  # Confirm permissions
    update_data = payload.dict(exclude_unset=True)
    if "transaction_id" in update_data:
        transaction = await session.get(Transaction, update_data["transaction_id"])
        if not transaction:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Transaction not found"
            )
    if "user_id" in update_data:
        user = await session.get(User, update_data["user_id"])
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    for key, value in update_data.items():
        setattr(transaction_message, key, value)
    session.add(transaction_message)
    await session.commit()
    await session.refresh(transaction_message)
    return transaction_message


# Delete
@router.delete(
    "/{transaction_message_id}",
    status_code=HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def delete_transaction_message(
    transaction_message_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    transaction_message = await session.get(TransactionMessage, transaction_message_id)
    if not transaction_message:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="TransactionMessage not found"
        )
    await confirm_auth_user(
        auth0_user,
        ["delete:transaction_messages"],
        session,
        user_id=transaction_message.user_id,
    )  # Confirm permissions
    await session.delete(transaction_message)
    await session.commit()
