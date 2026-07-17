import networkx as nx
import numpy as np
from geopandas import GeoDataFrame, GeoSeries
from shapely import MultiLineString, Point, STRtree
from momepy import gdf_to_nx
from networkx import relabel_nodes, Graph


from city_network.network_components import Connection, Node
from city_network.config import TransitMode


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