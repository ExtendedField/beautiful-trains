from schema import City, NetworkType
from networkx import MultiDiGraph
import os
import osmnx as ox

from settings import settings


def get_city_networks(city: City) -> tuple[MultiDiGraph, MultiDiGraph]:
    public_transit_network = _get_public_transit_network(city)
    walking_network = _get_walking_network(city)
    return public_transit_network, walking_network


def _get_public_transit_network(city: City) -> MultiDiGraph:
    return _get_graph_of_type(city, NetworkType.ALL_PUBLIC)


def _get_walking_network(city: City) -> MultiDiGraph:
    return _get_graph_of_type(city, NetworkType.WALK)


def _get_graph_of_type(city: City, network_type: NetworkType) -> MultiDiGraph:
    path = f"{settings.CACHE_LOCATION}{city.name}_{network_type.value}"
    if os.path.isfile(path):
        print(f"Data found at: {path}")
        return ox.io.load_graphml(path)
    print(f"No data found at: {path}. Downloading...")
    city_network = ox.graph.graph_from_place(
        city.open_street_map_city_name,
        network_type=network_type,
        simplify=True,
        retain_all=True,
    )
    print("Downloaded.")
    _save_network(city_network, path)
    return city_network


def _save_network(city_network: MultiDiGraph, path: str) -> None:
    print("Saving Data...")
    ox.io.save_graphml(G=city_network, filepath=path)
    print(f"Data Saved at {path}.")
