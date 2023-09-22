import os
from typing import Union

from fastapi import HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from app.models.user import User
from fastapi_auth0 import Auth0, Auth0User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


def get_auth():
    return Auth0(
        domain=os.environ.get("AUTH0_DOMAIN"),
        api_audience=os.environ.get("AUTH0_AUDIENCE"),
        scopes={
            "openid profile email": "Necessary to get email",
            "read:users": "Allows to read users other than own",
            "write:users": "Allows to create users",
            "modify:users": "Allows to modify users",
            "delete:users": "Allows to delete users",
            "read:products": "Allows to read products",
            "write:products": "Allows to create products",
            "modify:products": "Allows to modify products",
            "delete:products": "Allows to delete products",
            "read:wishes": "Allows to read wishes",
            "write:wishes": "Allows to create wishes",
            "modify:wishes": "Allows to modify wishes",
            "delete:wishes": "Allows to delete wishes",
            "read:likes": "Allows to read likes",
            "write:likes": "Allows to create likes",
            "modify:likes": "Allows to modify likes",
            "delete:likes": "Allows to delete likes",
            "read:comments": "Allows to read comments",
            "write:comments": "Allows to create comments",
            "modify:comments": "Allows to modify comments",
            "delete:comments": "Allows to delete comments",
            "read:offers": "Allows to read offers",
            "write:offers": "Allows to create offers",
            "modify:offers": "Allows to modify offers",
            "delete:offers": "Allows to delete offers",
            "read:transactions": "Allows to read transactions",
            "write:transactions": "Allows to create transactions",
            "modify:transactions": "Allows to modify transactions",
            "delete:transactions": "Allows to delete transactions",
            "read:areas": "Allows to read areas",
            "write:areas": "Allows to create areas",
            "modify:areas": "Allows to modify areas",
            "delete:areas": "Allows to delete areas",
            "read:matches": "Allows to read matches",
            "write:matches": "Allows to create matches",
            "modify:matches": "Allows to modify matches",
            "delete:matches": "Allows to delete matches",
            "read:match_messages": "Allows to read match_messages",
            "write:match_messages": "Allows to create match_messages",
            "modify:match_messages": "Allows to modify match_messages",
            "delete:match_messages": "Allows to delete match_messages",
            "read:transaction_messages": "Allows to read transaction_messages",
            "write:transaction_messages": "Allows to create transaction_messages",
            "modify:transaction_messages": "Allows to modify transaction_messages",
            "delete:transaction_messages": "Allows to delete transaction_messages",
            "read:categories": "Allows to read categories",
            "write:categories": "Allows to create categories",
            "modify:categories": "Allows to modify categories",
            "delete:categories": "Allows to delete categories",
            "read:brands": "Allows to read brands",
            "write:brands": "Allows to create brands",
            "modify:brands": "Allows to modify brands",
            "delete:brands": "Allows to delete brands",
            "read:images": "Allows to read images",
            "write:images": "Allows to create images",
            "modify:images": "Allows to modify images",
            "delete:images": "Allows to delete images",
        },
    )


async def confirm_auth_user(
    auth0_user: Auth0User,
    scope: list[str],
    session: AsyncSession,
    user_id: Union[int, list] = None,
):
    # Function to confirm permissions, and update Auth0 id if necessary
    # auth0_user: Auth0User
    # scope: list[str]
    # session: AsyncSession
    # user_id: int (optional, to confirm if the auth0_user is the same as the user_id)
    # return: User
    user = await session.execute(select(User).where(User.email == auth0_user.email))
    user = user.scalars().first()
    if isinstance(user_id, int):
        user_id = [user_id]
    if not all(sc in auth0_user.permissions for sc in scope):
        if not user_id or (user_id and user.id not in user_id):
            # Permission denied
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Permission denied"
            )
    if not user:
        # User not found
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Auth0 User not found in database"
        )
    if user.auth0_id != auth0_user.id:
        # Update user auth0_id
        user.auth0_id = auth0_user.id
        session.add(user)
        await session.commit()
        await session.refresh(user)
