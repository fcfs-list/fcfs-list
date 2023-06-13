from enum import Enum


class ProductCondition(str, Enum):
    bad = 'bad'
    acceptable = 'acceptable'
    normal = 'normal'
    good = 'good'
    like_new = 'like_new'
    new_unused = 'new_unused'

class ProductStatus(str, Enum):
    draft = 'draft'
    available = 'available'
    sold = 'sold'
    hidden = 'hidden'
    expired = 'expired'

class SellOrLend(str, Enum):
    sell = 'sell'
    lend = 'lend'
    both = 'both'

class SizeType(str, Enum):
    letter = 'letter'  # XS, S, M...
    tag = 'tag'
    clothes_EU = 'clothes_EU'  # 36, 38, 40...
    clothes_US = 'clothes_US'  # 2, 4, 6...
    clothes_UK = 'clothes_UK'  # 6, 8, 10...
    shoes_EU = 'shoes_EU'  # 35, 36...
    shoes_US = 'shoes_US'  # 6, 7, 8...
    shoes_UK = 'shoes_UK'  # 5, 6, 7...
    shoes_cm = 'shoes_cm'  # 24, 25, 26...

class OfferStatus(str, Enum):
    created = 'created'
    accepted = 'accepted'
    rejected = 'rejected'
    expired = 'expired'

class MatchStatus(str, Enum):
    created = 'created'
    accepted = 'accepted'
    rejected = 'rejected'
    expired = 'expired'

class TransactionStatus(str, Enum):
    created = 'created'
    paid = 'paid'
    cancelled = 'cancelled'
    completed = 'completed'
