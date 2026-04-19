from enum import Enum

from pydantic import BaseModel

class NetworkType(str, Enum):
    ALL_PUBLIC = "all_public"
    WALK = "walk"


class OpenStreetMapCityName(str, Enum):
    CHICAGO = "Chicago, Illinois, USA"
    ROSEBURG = "Roseburg, Oregon, USA"


class City(BaseModel):
    name: str
    open_street_map_city_name: str
