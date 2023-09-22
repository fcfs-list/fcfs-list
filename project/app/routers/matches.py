from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Security
from starlette.status import (
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from app.auth import get_auth, confirm_auth_user
from app.db import get_session
from app.models.match import (
    Match,
    MatchCreate,
    MatchRead,
    MatchReadFull,
    MatchUpdate,
)
from app.models.product import Product
from app.models.user import User
from app.models.wish import Wish
from app.utils.constants import (
    MATCH_DEFAULT_DEADLINE,
    MATCH_MAXIMUM_DEADLINE,
    MATCH_MINIMUM_DEADLINE,
)
from fastapi_auth0 import Auth0User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


router = APIRouter()


# List
@router.get(
    "/",
    response_model=list[MatchRead],
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def list_matches(
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["read:matches"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["read:matches"], session
    )  # Confirm permissions
    result = await session.execute(select(Match))
    matches = result.scalars().all()
    return matches


# Detail
@router.get(
    "/{match_id}",
    response_model=MatchReadFull,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def get_match(
    match_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    match = await session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Match not found")
    await confirm_auth_user(
        auth0_user,
        ["read:matches"],
        session,
        user_id=[match.user_id, match.product.user_id],
    )  # Confirm permissions
    return match


# Insert
@router.post(
    "/", response_model=MatchRead, dependencies=[Depends(get_auth().implicit_scheme)]
)
async def add_match(
    new_match: MatchCreate,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["write:matches"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["write:matches"], session
    )  # Confirm permissions
    if new_match.product_id is not None:
        product = await session.get(Product, new_match.product_id)
        if not product:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Product not found"
            )
    if new_match.user_id is not None:
        user = await session.get(User, new_match.user_id)
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    if new_match.wish_id is not None:
        wish = await session.get(Wish, new_match.wish_id)
        if not wish:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Wish not found")
    prod_matches = await session.execute(
        select(Match).where(Match.product_id == new_match.product_id)
    )
    prod_matches = prod_matches.scalars().all()
    existing_orders = [prod_match.order for prod_match in prod_matches]
    if new_match.order is not None:
        if new_match.order in existing_orders:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid order. Please select an order not included in the following: {}".format(
                    existing_orders
                ),
            )
    elif existing_orders:
        new_match.order = max(existing_orders) + 1
    else:
        new_match.order = 1
    if new_match.deadline is not None:
        if new_match.deadline < datetime.utcnow() + timedelta(
            days=MATCH_MINIMUM_DEADLINE
        ):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Deadline should be at least 24 hours later than the current time",
            )
        elif new_match.deadline > datetime.utcnow() + timedelta(
            days=MATCH_MAXIMUM_DEADLINE
        ):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Deadline should be at most 30 days later than the current time",
            )
    else:
        new_match.deadline = datetime.utcnow() + timedelta(days=MATCH_DEFAULT_DEADLINE)
    if new_match.product_id is not None and new_match.user_id is not None:
        existing_match = await session.execute(
            select(Match)
            .where(Match.product_id == new_match.product_id)
            .where(Match.user_id == new_match.user_id)
        )
        existing_match = existing_match.scalars().all()
        if existing_match:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="The given match already exists",
            )
    new_match = Match(**new_match.dict())
    session.add(new_match)
    await session.commit()
    await session.refresh(new_match)
    return new_match


# Update
@router.patch(
    "/{match_id}",
    response_model=MatchRead,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def update_match(
    match_id: int,
    payload: MatchUpdate,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    match = await session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Match not found")
    await confirm_auth_user(
        auth0_user,
        ["modify:matches"],
        session,
        user_id=[match.user_id, match.product.user_id],
    )  # Confirm permissions
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
    if "wish_id" in update_data:
        wish = await session.get(Wish, update_data["wish_id"])
        if not wish:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Wish not found")
    if "order" in update_data:
        product_id = update_data.get("product_id", match.product_id)
        prod_matches = await session.execute(
            select(Match).where(Match.product_id == product_id)
        )
        prod_matches = prod_matches.scalars().all()
        existing_orders = [prod_match.order for prod_match in prod_matches]
        if update_data["order"] in existing_orders:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid order. Please select an order not included in the following: {}".format(
                    existing_orders
                ),
            )
    if "deadline" in update_data:
        if update_data["deadline"] < datetime.utcnow() + timedelta(days=1):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Deadline should be at least 24 hours later than the current time",
            )
        elif update_data["deadline"] > datetime.utcnow() + timedelta(
            days=MATCH_MAXIMUM_DEADLINE
        ):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Deadline should be at most 30 days later than the current time",
            )
    if "product_id" in update_data or "user_id" in update_data:
        existing_match = await session.execute(
            select(Match)
            .where(Match.product_id == update_data.get("product_id", match.product_id))
            .where(Match.user_id == update_data.get("user_id", match.user_id))
        )
        existing_match = existing_match.scalars().all()
        if existing_match:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="The given match already exists",
            )
    for key, value in update_data.items():
        setattr(match, key, value)
    session.add(match)
    await session.commit()
    await session.refresh(match)
    _update_order(match.product_id, session)
    return match


# Delete
@router.delete("/{match_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_match(
    match_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    match = await session.get(Match, match_id)
    if not match:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Match not found")
    await confirm_auth_user(
        auth0_user,
        ["delete:matches"],
        session,
        user_id=[match.user_id, match.product.user_id],
    )  # Confirm permissions
    await session.delete(match)
    await session.commit()
    _update_order(match.product_id, session)


async def _update_order(
    product_id: int,
    session: AsyncSession,
    dependencies=[Depends(get_auth().implicit_scheme)],
):
    prod_matches = await session.execute(
        select(Match).where(Match.product_id == product_id).order_by(Match.order)
    )
    prod_matches = prod_matches.scalars().all()
    for i in range(len(prod_matches)):
        prod_matches[i].order = i + 1
    await session.commit()
