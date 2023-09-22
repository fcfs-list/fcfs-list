"""Brand Table Seeder """
import yaml


def seed_brand_table():
    with open("./app/seeders/fixtures/brands.yml", "r") as stream:
        try:
            data = yaml.load(stream, Loader=yaml.Loader)
            return data
        except yaml.YAMLError as exc:
            print(exc)
