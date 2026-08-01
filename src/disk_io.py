import json
import pickle
from pathlib import Path

from networkx import MultiDiGraph

from config.settings import settings
from schema import City, CityConfig


def get_city_config(city: str) -> CityConfig:
    with open("./config/city_config.json") as city_config_json:
        city_dict = json.load(city_config_json)[city]
        return CityConfig(
            name=city_dict.get("name", ""),
        )


def store_improved_transit_network(city: City, network: MultiDiGraph) -> None:
    path = Path(settings.CACHE_LOCATION) / f"improved_{city.name}.pkl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(network, f)
