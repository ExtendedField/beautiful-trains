from collect_data.schema import CityConfig
import json

# TODO: make this a pydantic schema not a dict
def initialize_client(city_config: dict):
    pass


def get_city_config(city: str) -> CityConfig:
    with open("./config/city_config.json") as city_config_json:
        city_dict = json.load(city_config_json)[city]
        return CityConfig(
            name=city_dict.get("name", ""),
            
        )
