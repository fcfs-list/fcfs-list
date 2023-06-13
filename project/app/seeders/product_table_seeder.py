"""Product Table Seeder """

from faker import Faker

from app.seeders.factories import ProductFactory

fake = Faker(['en_US', 'ja_JP'])
Faker.seed(0)

def seed_product_table(batch_size=500):
    products = ProductFactory.batch(size=batch_size, match_deadline = 48)

    products = [product.dict() for product in products]

    for i in range(len(products)):
        products[i]['id'] = i + 1
        products[i]['title'] = fake.unique.catch_phrase()
        products[i]['description'] = fake.unique.sentence()

    return products