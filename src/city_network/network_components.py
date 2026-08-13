from typing import NamedTuple

from pydantic import BaseModel
from shapely import Point


class Node(BaseModel):
    network_id: int
    location: Point

    class Config:
        arbitrary_types_allowed = True


class Connection(NamedTuple):
    node_1: Node
    node_2: Node
