from schema import City, NetworkType
from networkx import MultiDiGraph
import osmnx as ox


def get_public_transit_network(city: City) -> MultiDiGraph:
    return _get_graph_of_type(city, NetworkType.ALL_PUBLIC)


def get_walking_network(city: City) -> MultiDiGraph:
    return _get_graph_of_type(city, NetworkType.WALK)


def _get_graph_of_type(city: City, network_type: NetworkType) -> MultiDiGraph:
    return ox.graph.graph_from_place(
        city.open_street_map_city_name,
        network_type=network_type,
        simplify=True,
        retain_all=True,
    )


def save_network(city: City, city_network: MultiDiGraph) -> None:
    print("Saving Data...")
    target_dir = f"../network_cache/{city.name}"
    ox.io.save_graphml(G=city_network, filepath=target_dir)
    print(f"Data Saved at {target_dir}.")


### TODO: validate incoming data with decorators maybe could be cool
# def _validate(meta_data_schema: Type[ComponentMetaData]):
#     def validated(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             meta_data_schema.model_validate(**kwargs)
#             return func(*args, **kwargs)
#         return wrapper
#     return validated
