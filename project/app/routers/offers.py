from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Security
from starlette.status import (
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from app.auth import get_auth, confirm_auth_user
from app.db import get_session
from app.models.offer import Offer, OfferCreate, OfferRead, OfferUpdate
from app.models.product import Product
from app.models.user import User
from app.utils.constants import (
    OFFER_DEFAULT_DEADLINE,
    OFFER_MAXIMUM_DEADLINE,
    OFFER_MINIMUM_DEADLINE,
)
from app.utils.enums import OfferStatus
from fastapi_auth0 import Auth0User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


router = APIRouter()


# List
@router.get(
    "/",
    response_model=list[OfferRead],
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def list_offers(
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["read:offers"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(auth0_user, ["read:offers"], session)  # Confirm permissions
    result = await session.execute(select(Offer))
    offers = result.scalars().all()
    return offers


# Detail
@router.get(
    "/{offer_id}",
    response_model=OfferRead,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def get_offer(
    offer_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    offer = await session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Offer not found")
    await confirm_auth_user(
        auth0_user,
        ["read:offers"],
        session,
        user_id=[offer.user_id, offer.product.user_id],
    )  # Confirm permissions
    return offer


# Insert
@router.post(
    "/", response_model=OfferRead, dependencies=[Depends(get_auth().implicit_scheme)]
)
async def add_offer(
    new_offer: OfferCreate,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["write:offers"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["write:offers"], session
    )  # Confirm permissions
    if new_offer.product_id is not None:
        product = await session.get(Product, new_offer.product_id)
        if not product:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Product not found"
            )
    if new_offer.user_id is not None:
        user = await session.get(User, new_offer.user_id)
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
    prod_offers = await session.execute(
        select(Offer).where(Offer.product_id == new_offer.product_id)
    )
    prod_offers = prod_offers.scalars().all()
    existing_orders = [prod_offer.order for prod_offer in prod_offers]
    if new_offer.order is not None:
        if new_offer.order in existing_orders:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid order. Please select an order not included in the following: {}".format(
                    existing_orders
                ),
            )
    elif existing_orders:
        new_offer.order = max(existing_orders) + 1
    else:
        new_offer.order = 1
    if new_offer.deadline is not None:
        if new_offer.deadline < datetime.utcnow() + timedelta(
            days=OFFER_MINIMUM_DEADLINE
        ):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Deadline should be at least 24 hours later than the current time",
            )
        elif new_offer.deadline > datetime.utcnow() + timedelta(
            days=OFFER_MAXIMUM_DEADLINE
        ):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Deadline should be at most 30 days later than the current time",
            )
    else:
        new_offer.deadline = datetime.utcnow() + timedelta(days=OFFER_DEFAULT_DEADLINE)
    if new_offer.product_id is not None and new_offer.user_id is not None:
        existing_offer = await session.execute(
            select(Offer)
            .where(Offer.product_id == new_offer.product_id)
            .where(Offer.user_id == new_offer.user_id)
            .where(Offer.status == OfferStatus.created)
        )
        existing_offer = existing_offer.scalars().all()
        if existing_offer:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="There is already an active offer from the same user for the same product",
            )
    new_offer = Offer(**new_offer.dict())
    session.add(new_offer)
    await session.commit()
    await session.refresh(new_offer)
    return new_offer


# Update
@router.patch(
    "/{offer_id}",
    response_model=OfferRead,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def update_offer(
    offer_id: int,
    payload: OfferUpdate,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    offer = await session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Offer not found")
    await confirm_auth_user(
        auth0_user,
        ["modify:offers"],
        session,
        user_id=[offer.user_id, offer.product.user_id],
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
    if "order" in update_data:
        product_id = update_data.get("product_id", offer.product_id)
        prod_offers = await session.execute(
            select(Offer).where(Offer.product_id == product_id)
        )
        prod_offers = prod_offers.scalars().all()
        existing_orders = [prod_offer.order for prod_offer in prod_offers]
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
            days=OFFER_MAXIMUM_DEADLINE
        ):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Deadline should be at most 30 days later than the current time",
            )
    if "product_id" in update_data or "user_id" in update_data:
        existing_offer = await session.execute(
            select(Offer)
            .where(Offer.product_id == update_data.get("product_id", offer.product_id))
            .where(Offer.user_id == update_data.get("user_id", offer.user_id))
            .where(Offer.status == OfferStatus.created)
        )
        existing_offer = existing_offer.scalars().all()
        if existing_offer:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="There is already an active offer from the same user for the same product",
            )
    for key, value in update_data.items():
        setattr(offer, key, value)
    session.add(offer)
    await session.commit()
    await session.refresh(offer)
    return offer


# Delete
@router.delete(
    "/{offer_id}",
    status_code=HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def delete_offer(
    offer_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["delete:offers"]),
    session: AsyncSession = Depends(get_session),
):
    offer = await session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Offer not found")
    await confirm_auth_user(
        auth0_user,
        ["delete:offers"],
        session,
        user_id=[offer.user_id, offer.product.user_id],
    )  # Confirm permissions
    await session.delete(offer)
    await session.commit()
