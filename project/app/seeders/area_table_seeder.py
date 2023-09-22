"""Area Table Seeder"""
import yaml


def seed_area_table():
    with open("./app/seeders/fixtures/areas.yml", "r") as stream:
        try:
            data = yaml.load(stream, Loader=yaml.Loader)
            return data
        except yaml.YAMLError as exc:
            print(exc)
