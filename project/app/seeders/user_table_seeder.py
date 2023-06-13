"""User Table Seeder """
import bcrypt

from faker import Faker

from app.seeders.factories import UserFactory

fake = Faker(['en_US', 'ja_JP'])
Faker.seed(0)

def seed_user_table(batch_size=50):
    users = UserFactory.batch(
        size=batch_size,
        password=bcrypt.hashpw('secret'.encode('utf-8'),
        bcrypt.gensalt()),
        phone=None,
        is_admin=False,
        deleted_at=None
    )

    users = [user.dict() for user in users]

    processed_emails = []

    for i in range(len(users)):
        users[i]['id'] = i + 1
        users[i]['name'] = fake.unique.name()
        users[i]['email'] = fake.unique.email()
        users[i]['password'] = users[i]['password'].get_secret_value()
        while users[i]['email'] in processed_emails:
            users[i]['email'] = 's%s' % users[i]['email']
        processed_emails.append(users[i]['email'])

    return users