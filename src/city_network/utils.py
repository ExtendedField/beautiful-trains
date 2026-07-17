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


def connect_spacial_graph(g: Graph) -> None:
    tree = STRtree([Point(node.longitude, node.latitude) for node in g])
    connect_graph_using_tree(g, tree)


def connect_graph_using_tree(
    graph: Graph,
    tree: STRtree,
    min_dist: float = 0.005,
    max_dist: float = 1,
    increment: float = 0.005,
) -> nx.Graph | None:
    if nx.is_connected(graph):
        return graph
    else:
        node_list = np.array(list(graph.nodes()))
        largest_subgraph = max(nx.connected_components(graph), key=len)
        disconnected_subgraphs = [
            graph.subgraph(subgraph)
            for subgraph in nx.connected_components(graph)
            if len(subgraph) < len(largest_subgraph)
        ]
        target = disconnected_subgraphs[0]
        nodes_in_largest_subgraph = list(target.nodes())
        starting = nodes_in_largest_subgraph[0]
        valid_targs = []
        while (min_dist < max_dist) & (len(valid_targs) < 1):
            valid_targs += [
                node
                for node in node_list[
                    tree.query(
                        starting.location, predicate="dwithin", distance=min_dist
                    )
                ]
                if node not in nodes_in_largest_subgraph
            ]
            min_dist += increment
        ending = valid_targs[0]
        u, v, connection_data = Connection(
            station1=starting,
            station2=ending,
            transit_modes=[TransitMode.WALK],
        ).get_weighted_tuple()
        graph.add_edge(u, v, **connection_data)
        connect_graph_using_tree(graph, tree)
