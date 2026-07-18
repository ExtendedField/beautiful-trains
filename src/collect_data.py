from utils import connect_spacial_graph
from pathlib import Path

from networkx import MultiDiGraph
import os
import osmnx as ox


from schema import City
from config.library import NetworkType
from config.settings import settings


def get_city_networks(city: City) -> tuple[MultiDiGraph, MultiDiGraph]:
    public_transit_network = _get_public_transit_network(city)
    walking_network = _get_walking_network(city)
    return public_transit_network, walking_network


def _get_public_transit_network(city: City) -> MultiDiGraph:
    return _get_graph_of_type(city, NetworkType.ALL_PUBLIC)


def _get_walking_network(city: City) -> MultiDiGraph:
    return _get_graph_of_type(city, NetworkType.WALK)


def _get_graph_of_type(city: City, network_type: NetworkType) -> MultiDiGraph:
    path = settings.CACHE_LOCATION / city.name / network_type.value
    if os.path.isfile(path):
        print(f"Data found at: {path}")
        city_network = ox.io.load_graphml(path)
        connect_spacial_graph(city_network)
        return city_network
    print(f"No data found at: {path}. Downloading...")
    city_network = ox.graph.graph_from_place(
        city.open_street_map_city_name,
        network_type=network_type,
        simplify=True,
        retain_all=True,
    )
    print("Downloaded.")
    connect_spacial_graph(city_network)  # TODO: verify this edits in place successfully
    _save_network(city_network, path)
    return city_network


def _save_network(city_network: MultiDiGraph, path: Path) -> None:
    print("Saving Data...")
    ox.io.save_graphml(G=city_network, filepath=path)
    print(f"Data Saved at {path}.")
