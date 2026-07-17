import pickle
import json
from pathlib import Path

from networkx import MultiDiGraph
from schema import City

from schema import CityConfig
from settings import settings


def get_city_config(city: str) -> CityConfig:
    with open("./config/city_config.json") as city_config_json:
        city_dict = json.load(city_config_json)[city]
        return CityConfig(
            name=city_dict.get("name", ""),
        )


def store_improved_transit_network(city: City, network: MultiDiGraph) -> None:
    path = Path("..") / settings.CACHE_LOCATION / f"improved_{city.name}.pkl"
    with open(path, "wb") as f:
        pickle.dump(network, f)
