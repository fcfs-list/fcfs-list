from .area import Area
from .brand import Brand
from .category import Category
from .comment import Comment
from .image import Image
from .like import Like
from .match import Match
from .match_message import MatchMessage
from .offer import Offer
from .product import Product
from .product_area import ProductArea
from .product_category import ProductCategory
from .transaction import Transaction
from .transaction_message import TransactionMessage
from .user import User
from .user_area import UserArea
from .wish import Wish
from .wish_area import WishArea
from .wish_brand import WishBrand
from .wish_category import WishCategory


# Area.update_forward_refs(Area=Area, User=User, Product=Product, Wish=Wish)
# AreaReadFull.update_forward_refs(AreaRead=AreaRead, UserRead=UserRead, ProductRead=ProductRead, WishRead=WishRead)
# Brand.update_forward_refs(Product=Product, Wish=Wish)
# Category.update_forward_refs(Category=Category, Product=Product, Wish=Wish)
# CategoryReadFull.update_forward_refs(CategoryRead=CategoryRead)
# Comment.update_forward_refs(User=User, Product=Product)
# Image.update_forward_refs(Product=Product)
# Like.update_forward_refs(User=User, Product=Product)
# MatchMessage.update_forward_refs(User=User, Match=Match)
# Match.update_forward_refs(User=User, Product=Product, Wish=Wish, MatchMessage=MatchMessage)
# MatchReadFull.update_forward_refs(UserRead=UserRead, ProductRead=ProductRead, WishRead=WishRead, MatchMessageRead=MatchMessageRead)
# Offer.update_forward_refs(User=User, Product=Product)
# Product.update_forward_refs(
#     User=User, Brand=Brand, Comment=Comment, Like=Like, Match=Match, Image=Image, Offer=Offer,
#     Transaction=Transaction, Category=Category, Area=Area
# )
# ProductReadFull.update_forward_refs(
#     UserRead=UserRead, BrandRead=BrandRead, CommentRead=CommentRead, LikeRead=LikeRead, MatchRead=MatchRead,
#     ImageRead=ImageRead, OfferRead=OfferRead, TransactionRead=TransactionRead, CategoryRead=CategoryRead, AreaRead=AreaRead
# )
# TransactionMessage.update_forward_refs(User=User, Transaction=Transaction)
# Transaction.update_forward_refs(User=User, Product=Product, TransactionMessage=TransactionMessage)
# TransactionReadFull.update_forward_refs(UserRead=UserRead, ProductRead=ProductRead, TransactionMessageRead=TransactionMessageRead)
# User.update_forward_refs(
#     Product=Product, Wish=Wish, Comment=Comment, Like=Like, Match=Match, MatchMessage=MatchMessage, Offer=Offer,
#     Transaction=Transaction, TransactionMessage=TransactionMessage, Area=Area
# )
# UserReadFull.update_forward_refs(
#     ProductRead=ProductRead, WishRead=WishRead, CommentRead=CommentRead, LikeRead=LikeRead,
#     MatchRead=MatchRead, MatchMessageRead=MatchMessageRead, OfferRead=OfferRead, TransactionRead=TransactionRead,
#     TransactionMessageRead=TransactionMessageRead, AreaRead=AreaRead
# )
# Wish.update_forward_refs(User=User, Brand=Brand, Match=Match, Category=Category, Area=Area)
# WishReadFull.update_forward_refs(
#     UserRead=UserRead, BrandRead=BrandRead, MatchRead=MatchRead, CategoryRead=CategoryRead, AreaRead=AreaRead
# )
