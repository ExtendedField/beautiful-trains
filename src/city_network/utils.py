import networkx as nx
from geopandas import GeoDataFrame, GeoSeries
from momepy import gdf_to_nx
from networkx import Graph, relabel_nodes
from shapely import MultiLineString, Point

from city_network.network_components import Node


def graph_from_shapes(shapes: MultiLineString, relabel_mapping: dict = {}) -> Graph:
    gdf_shapes = GeoDataFrame(geometry=GeoSeries(shapes).explode())
    graph = gdf_to_nx(gdf_shapes)
    graph = relabel_nodes(graph, relabel_mapping)
    graph = nx.from_edgelist(  # TODO: convert walking graph to always use nodes
        [
            (
                Node(net_id="", location=Point(u[0], u[1])),
                Node(net_id="", location=Point(v[0], v[1])),
            )
            for u, v in graph.edges()
        ]
    )
    return graph
