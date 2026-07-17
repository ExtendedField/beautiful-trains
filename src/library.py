from enum import Enum


class NetworkType(str, Enum):
    ALL_PUBLIC = "all_public"
    WALK = "walk"


class OpenStreetMapCityName(str, Enum):
    CHICAGO = "Chicago, Illinois, USA"
    ROSEBURG = "Roseburg, Oregon, USA"
