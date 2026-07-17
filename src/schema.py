from pydantic import BaseModel


class City(BaseModel):
    name: str
    open_street_map_city_name: str


class CityConfig(BaseModel):
    name: str
