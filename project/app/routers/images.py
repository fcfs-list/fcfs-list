import os
import imghdr
from fastapi import APIRouter, Depends, HTTPException, Security, File, UploadFile
from starlette.status import (
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)
from google.cloud import storage
from google.api_core.exceptions import NotFound

from app.auth import get_auth, confirm_auth_user
from app.db import get_session
from app.models.image import Image, ImageCreate, ImageRead, ImageUpdate
from app.models.product import Product
from fastapi_auth0 import Auth0User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select


router = APIRouter()


# List
@router.get(
    "/images",
    response_model=list[ImageRead],
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def list_images(
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["read:images"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(auth0_user, ["read:images"], session)  # Confirm permissions
    result = await session.execute(select(Image))
    images = result.scalars().all()
    return images


# List by product
@router.get(
    "/products/{product_id}/images",
    response_model=list[ImageRead],
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def list_images(
    product_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["read:images"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(auth0_user, ["read:images"], session)  # Confirm permissions
    result = await session.execute(select(Image).where(Image.product_id == product_id))
    images = result.scalars().all()
    return images


# Detail
@router.get(
    "/images/{image_id}",
    response_model=ImageRead,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
@router.get(
    "/products/{product_id}/images/{image_id}",
    response_model=ImageRead,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def get_image(
    image_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["read:images"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(auth0_user, ["read:images"], session)  # Confirm permissions
    image = await session.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Image not found")
    return image


# Function to insert image in db
async def _insert_image_in_db(
    new_image: ImageCreate,
    session: AsyncSession = Depends(get_session),
):
    new_image = Image(**new_image.dict())
    session.add(new_image)
    await session.commit()
    await session.refresh(new_image)
    return new_image


# Upload image and insert in db
@router.post(
    "/products/{product_id}/images",
    response_model=list[ImageRead],
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def add_images(
    product_id: int,
    files: list[UploadFile] = File(...),
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["write:images"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["write:images"], session
    )  # Confirm permissions
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Product not found")
    prod_images = await session.execute(
        select(Image).where(Image.product_id == product_id)
    )
    prod_images = prod_images.scalars().all()
    existing_orders = [prod_image.order for prod_image in prod_images]
    new_image_order = 1
    if existing_orders:
        new_image_order = max(existing_orders) + 1
    # Authenticate with GCP
    client = storage.Client()
    # Set the name of the bucket you want to upload to
    bucket = client.get_bucket(os.getenv("GCS_BUCKET"))
    result = []
    for file in files:
        # Check if the file is an image
        if imghdr.what(file.file) is None:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, detail="File is not an image"
            )
        # Set the name of the file you want to upload
        blob = bucket.blob(file.filename)
        # Upload the file to GCS
        blob.upload_from_file(file.file)
        # Get the uploaded file's URL
        url = f"https://storage.googleapis.com/{bucket.name}/{blob.name}"
        # Create the image in the database
        new_image = ImageCreate(url=url, product_id=product_id, order=new_image_order)
        new_image_order += 1
        inserted_image = await _insert_image_in_db(new_image, session)
        result.append(inserted_image)
    # Return the list of images
    return result


# Update
@router.patch(
    "/images/{image_id}",
    response_model=ImageRead,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
@router.patch(
    "/products/{product_id}/images/{image_id}",
    response_model=ImageRead,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def update_image(
    image_id: int,
    payload: ImageUpdate,
    auth0_user: Auth0User = Security(get_auth().get_user, scopes=["modify:images"]),
    session: AsyncSession = Depends(get_session),
):
    await confirm_auth_user(
        auth0_user, ["modify:images"], session
    )  # Confirm permissions
    image = await session.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Image not found")
    update_data = payload.dict(exclude_unset=True)
    if "product_id" in update_data:
        product = await session.get(Product, update_data["product_id"])
        if not product:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail="Product not found"
            )
    if "order" in update_data:
        product_id = update_data.get("product_id", image.product_id)
        prod_images = await session.execute(
            select(Image).where(Image.product_id == product_id)
        )
        prod_images = prod_images.scalars().all()
        existing_orders = [prod_image.order for prod_image in prod_images]
        if update_data["order"] in existing_orders:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid order. Please select an order not included in the following: {}".format(
                    existing_orders
                ),
            )
    for key, value in update_data.items():
        setattr(image, key, value)
    session.add(image)
    await session.commit()
    await session.refresh(image)
    return image


# Delete
@router.delete(
    "/{image_id}",
    status_code=HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_auth().implicit_scheme)],
)
async def delete_image(
    image_id: int,
    auth0_user: Auth0User = Security(get_auth().get_user),
    session: AsyncSession = Depends(get_session),
):
    image = await session.get(Image, image_id)
    await confirm_auth_user(
        auth0_user, ["delete:images"], session, user_id=image.product.user_id
    )  # Confirm permissions
    if not image:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Image not found")
    # Authenticate with GCP
    client = storage.Client()
    # Get the name of the bucket and the name of the blob from the URL
    bucket_name = image.url.split("/")[3]
    blob_name = "/".join(image.url.split("/")[4:])
    # Get the bucket and the blob
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    # Delete the blob
    try:
        blob.delete()
    except NotFound:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail="Image not found in GCS"
        )
    await session.delete(image)
    await session.commit()
