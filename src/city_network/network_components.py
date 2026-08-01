from pydantic import BaseModel
from shapely import Point


class Node(BaseModel):
    network_id: int
    location: Point

    class Config:
        arbitrary_types_allowed = True
