from shapely import Point
from pydantic import BaseModel


class Node(BaseModel):
    network_id: int
    location: Point

    class Config:
        arbitrary_types_allowed = True
