"""Category Table Seeder """
import yaml

def seed_category_table_clothing():
    # seeder = ResolvingSeeder(anext(get_session()))
    with open('./app/seeders/fixtures/categories_clothing.yml', 'r') as stream:
        try:
            data = yaml.load(stream, Loader=yaml.Loader)
            return data
        except yaml.YAMLError as exc:
            print(exc)
