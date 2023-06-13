import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite
from fastapi_amis_admin.admin import admin
from fastapi.responses import JSONResponse
from pydantic.error_wrappers import ValidationError
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from sqlmodel.sql.expression import Select

from .models import (
    Area, Brand, Category, Comment, Image, Like, MatchMessage, Match, Offer, ProductArea, ProductCategory,
    Product, TransactionMessage, Transaction, UserArea, User, WishArea, WishBrand, WishCategory, Wish
)
from .routers import (
    areas, brands, categories, products, comments, likes, matches, match_messages,
    offers, transactions, transaction_messages, wishes, users
)

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=['http://localhost:8080'],
#     allow_credentials=True,
#     allow_methods=['*'],
#     allow_headers=['*']
# )

# Iclude routers for APIs
app.include_router(categories.router, tags=['categories'], prefix='/v1/categories', responses={HTTP_404_NOT_FOUND: {'description': 'Not found'}})
app.include_router(areas.router, tags=['areas'], prefix='/v1/areas', responses={HTTP_404_NOT_FOUND: {'description': 'Not found'}})
app.include_router(brands.router, tags=['brands'], prefix='/v1/brands', responses={HTTP_404_NOT_FOUND: {'description': 'Not found'}})
app.include_router(products.router, tags=['products'], prefix='/v1/products', responses={HTTP_404_NOT_FOUND: {'description': 'Not found'}})
app.include_router(comments.router, tags=['comments'], prefix='/v1/comments', responses={HTTP_404_NOT_FOUND: {'description': 'Not found'}})
app.include_router(likes.router, tags=['likes'], prefix='/v1/likes', responses={HTTP_404_NOT_FOUND: {'description': 'Not found'}})
app.include_router(matches.router, tags=['matches'], prefix='/v1/matches', responses={HTTP_404_NOT_FOUND: {'description': 'Not found'}})
app.include_router(match_messages.router,
    tags=['match_messages', 'matchmessages'], prefix='/v1/matchmessages', responses={HTTP_404_NOT_FOUND: {'description': 'Not found'}})
app.include_router(offers.router, tags=['offers'], prefix='/v1/offers', responses={HTTP_404_NOT_FOUND: {'description': 'Not found'}})
app.include_router(transactions.router, tags=['transactions'], prefix='/v1/transactions', responses={HTTP_404_NOT_FOUND: {'description': 'Not found'}})
app.include_router(transaction_messages.router,
    tags=['transaction_messages', 'transactionmessages'], prefix='/v1/transactionmessages', responses={HTTP_404_NOT_FOUND: {'description': 'Not found'}})
app.include_router(wishes.router, tags=['wishes'], prefix='/v1/wishes', responses={HTTP_404_NOT_FOUND: {'description': 'Not found'}})
app.include_router(users.router, tags=['users'], prefix='/v1/users', responses={HTTP_404_NOT_FOUND: {'description': 'Not found'}})

# Add error handling
@app.exception_handler(ValidationError)
async def validation_error_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={'message': str(exc)},
    )

# Create AdminSite instance
site = AdminSite(settings=Settings(database_url_async=os.environ.get('DATABASE_URL')))

# Register ModelAdmin
@site.register_admin
class AreaAdmin(admin.ModelAdmin):
    page_schema = 'Area Management'
    # Configuration management model
    model = Area
    list_display = [
        Area.parent_id, Area.name_en, Area.name_ja, Area.radius_km, Area.latitude, Area.longitude, User.name
    ]
    search_fields = [Area.name_en, Area.name_ja]

    # custom base selector
    async def get_select(self, request: Request) -> Select:
        stmt = await super().get_select(request)
        return stmt.outerjoin(User, User.id == Area.created_by)

@site.register_admin
class BrandAdmin(admin.ModelAdmin):
    page_schema = 'Brand Management'
    # Configuration management model
    model = Brand
    list_display = [Brand.name_en, Brand.name_ja]
    search_fields = [Brand.name_en, Brand.name_ja]

@site.register_admin
class CategoryAdmin(admin.ModelAdmin):
    page_schema = 'Category Management'
    # Configuration management model
    model = Category
    list_display = [
        Category.parent_id, Category.level, Category.name_en, Category.description_en,
        Category.name_ja, Category.description_ja
    ]
    search_fields = [Category.name_en, Category.name_ja]

@site.register_admin
class CommentAdmin(admin.ModelAdmin):
    page_schema = 'Comment Management'
    # Configuration management model
    model = Comment
    list_display = [Comment.comment, User.name, Product.title, Comment.user_id, Comment.product_id]
    search_fields = [Comment.comment]

    # custom base selector
    async def get_select(self, request: Request) -> Select:
        stmt = await super().get_select(request)
        return stmt.outerjoin(User, User.id == Comment.user_id).outerjoin(Product, Product.id == Comment.product_id)

@site.register_admin
class ImageAdmin(admin.ModelAdmin):
    page_schema = 'Image Management'
    # Configuration management model
    model = Image
    list_display = [Image.url, Image.product_id, Product.title]
    search_fields = [Product.title]

    # custom base selector
    async def get_select(self, request: Request) -> Select:
        stmt = await super().get_select(request)
        return stmt.outerjoin(Product, Product.id == Image.product_id)

@site.register_admin
class LikeAdmin(admin.ModelAdmin):
    page_schema = 'Like Management'
    # Configuration management model
    model = Like
    list_display = [User.name, Product.title, Like.user_id, Like.product_id]
    search_fields = [Product.title, User.name]

    # custom base selector
    async def get_select(self, request: Request) -> Select:
        stmt = await super().get_select(request)
        return stmt.outerjoin(User, User.id == Like.user_id).outerjoin(Product, Product.id == Like.product_id)

@site.register_admin
class MatchAdmin(admin.ModelAdmin):
    page_schema = 'Match Management'
    # Configuration management model
    model = Match
    list_display = [User.name, Product.title, Match.user_id, Match.product_id, Match.wish_id, Match.order, Match.status, Match.deadline]
    search_fields = [Product.title, User.name, Match.status]

    # custom base selector
    async def get_select(self, request: Request) -> Select:
        stmt = await super().get_select(request)
        return stmt.outerjoin(User, User.id == Match.user_id).outerjoin(Product, Product.id == Match.product_id)

@site.register_admin
class MatchMessageAdmin(admin.ModelAdmin):
    page_schema = 'MatchMessage Management'
    # Configuration management model
    model = MatchMessage
    list_display = [MatchMessage.content, User.name, MatchMessage.user_id, MatchMessage.match_id]
    search_fields = [MatchMessage.content]

    # custom base selector
    async def get_select(self, request: Request) -> Select:
        stmt = await super().get_select(request)
        return stmt.outerjoin(User, User.id == MatchMessage.user_id)

@site.register_admin
class OfferAdmin(admin.ModelAdmin):
    page_schema = 'Offer Management'
    # Configuration management model
    model = Offer
    list_display = [
        Offer.amount, Product.currency, User.name, Product.title, Offer.user_id, Offer.product_id,
        Offer.order, Offer.status, Offer.deadline
    ]
    search_fields = [Offer.amount, Product.title, User.name, Offer.status]

    # custom base selector
    async def get_select(self, request: Request) -> Select:
        stmt = await super().get_select(request)
        return stmt.outerjoin(User, User.id == Offer.user_id).outerjoin(Product, Product.id == Offer.product_id)

@site.register_admin
class ProductAreaAdmin(admin.ModelAdmin):
    page_schema = 'ProductArea Management'
    # Configuration management model
    model = ProductArea
    list_display = [Area.name_en, Area.name_ja, Product.title, ProductArea.area_id, ProductArea.product_id]
    search_fields = [Product.title, Area.name_en, Area.name_ja]

    # custom base selector
    async def get_select(self, request: Request) -> Select:
        stmt = await super().get_select(request)
        return stmt.outerjoin(Area, Area.id == ProductArea.area_id).outerjoin(Product, Product.id == ProductArea.product_id)

@site.register_admin
class ProductCategoryAdmin(admin.ModelAdmin):
    page_schema = 'ProductCategory Management'
    # Configuration management model
    model = ProductCategory
    list_display = [Category.name_en, Category.name_ja, Product.title, ProductCategory.category_id, ProductArea.product_id]
    search_fields = [Product.title, Category.name_en, Category.name_ja]

    # custom base selector
    async def get_select(self, request: Request) -> Select:
        stmt = await super().get_select(request)
        return stmt.outerjoin(
            Category, Category.id == ProductCategory.category_id).outerjoin(Product, Product.id == ProductCategory.product_id)

@site.register_admin
class ProductAdmin(admin.ModelAdmin):
    page_schema = 'Product Management'
    # Configuration management model
    model = Product
    list_display = [
        Product.title, Product.description, Product.price, Product.currency, Product.condition,
        Product.sell_or_lend, Product.lend_period, Product.status, Product.size_type, Product.size,
        Product.user_id, User.name, Product.brand_id, Brand.name_en, Brand.name_ja, Product.immediate_deal,
        Product.negotiable, Product.match_deadline
    ]
    search_fields = [Product.title, Product.currency, Product.status, Brand.name_en, Brand.name_ja, User.name]

    # custom base selector
    async def get_select(self, request: Request) -> Select:
        stmt = await super().get_select(request)
        return stmt.outerjoin(User, User.id == Product.user_id).outerjoin(Brand, Brand.id == Product.brand_id)

@site.register_admin
class TransactionAdmin(admin.ModelAdmin):
    page_schema = 'Transaction Management'
    # Configuration management model
    model = Transaction
    list_display = [User.name, Product.title, Transaction.buyer_id, Transaction.product_id, Transaction.status]
    search_fields = [Product.title, User.name, Transaction.status]

    # custom base selector
    async def get_select(self, request: Request) -> Select:
        stmt = await super().get_select(request)
        return stmt.outerjoin(User, User.id == Transaction.buyer_id).outerjoin(Product, Product.id == Transaction.product_id)

@site.register_admin
class TransactionMessageAdmin(admin.ModelAdmin):
    page_schema = 'TransactionMessage Management'
    # Configuration management model
    model = TransactionMessage
    list_display = [TransactionMessage.content, User.name, TransactionMessage.user_id, TransactionMessage.transaction_id]
    search_fields = [TransactionMessage.content]

    # custom base selector
    async def get_select(self, request: Request) -> Select:
        stmt = await super().get_select(request)
        return stmt.outerjoin(User, User.id == TransactionMessage.user_id)

@site.register_admin
class UserAreaAdmin(admin.ModelAdmin):
    page_schema = 'UserArea Management'
    # Configuration management model
    model = UserArea
    list_display = [Area.name_en, Area.name_ja, User.name, UserArea.area_id, UserArea.user_id]
    search_fields = [User.name, Area.name_en, Area.name_ja]

    # custom base selector
    async def get_select(self, request: Request) -> Select:
        stmt = await super().get_select(request)
        return stmt.outerjoin(Area, Area.id == UserArea.area_id).outerjoin(User, User.id == UserArea.user_id)

@site.register_admin
class UserAdmin(admin.ModelAdmin):
    page_schema = 'User Management'
    # Configuration management model
    model = User
    list_display = [User.name, User.email, User.phone, User.is_admin, User.verified_at]
    search_fields = [User.name, User.email, User.phone, User.is_admin]

@site.register_admin
class WishAreaAdmin(admin.ModelAdmin):
    page_schema = 'WishArea Management'
    # Configuration management model
    model = WishArea
    list_display = [Area.name_en, Area.name_ja, WishArea.area_id, WishArea.wish_id]
    search_fields = [Area.name_en, Area.name_ja]

    # custom base selector
    async def get_select(self, request: Request) -> Select:
        stmt = await super().get_select(request)
        return stmt.outerjoin(Area, Area.id == WishArea.area_id)

@site.register_admin
class WishBrandAdmin(admin.ModelAdmin):
    page_schema = 'WishBrand Management'
    # Configuration management model
    model = WishBrand
    list_display = [Brand.name_en, Brand.name_ja, WishBrand.brand_id, WishBrand.wish_id]
    search_fields = [Brand.name_en, Brand.name_ja]

    # custom base selector
    async def get_select(self, request: Request) -> Select:
        stmt = await super().get_select(request)
        return stmt.outerjoin(Brand, Brand.id == WishBrand.brand_id)

@site.register_admin
class WishCategoryAdmin(admin.ModelAdmin):
    page_schema = 'WishCategory Management'
    # Configuration management model
    model = WishCategory
    list_display = [Category.name_en, Category.name_ja, WishCategory.category_id, WishCategory.wish_id]
    search_fields = [Category.name_en, Category.name_ja]

    # custom base selector
    async def get_select(self, request: Request) -> Select:
        stmt = await super().get_select(request)
        return stmt.outerjoin(Category, Category.id == WishCategory.category_id)

@site.register_admin
class WishAdmin(admin.ModelAdmin):
    page_schema = 'Wish Management'
    # Configuration management model
    model = Wish
    list_display = [
        Wish.keywords, Wish.user_id, User.name
    ]
    search_fields = [Wish.keywords, User.name]

    # custom base selector
    async def get_select(self, request: Request) -> Select:
        stmt = await super().get_select(request)
        return stmt.outerjoin(User, User.id == Wish.user_id)

# Mount the background management system
site.mount_app(app)

# Default endpoint, just to confirm the API works correctly
@app.get('/')
async def home():
    return 'Welcome to Kashikally API!'