import networkx as nx
import numpy as np
from geopandas import GeoSeries
from shapely import MultiLineString
from momepy import gdf_to_nx
from networkx import relabel_nodes, Graph

from city_network.network_components import Connection


def graph_from_shapes(shapes: MultiLineString, relabel_mapping: dict = {}) -> Graph:
    graph = gdf_to_nx(GeoSeries(shapes).explode())
    graph = relabel_nodes(graph, relabel_mapping)
    return graph


def connect_graph(g, tree):
    """
    Takes a disconnected graph and recursively stitches it back together to create a fully connected graph by connecting
    close points on two disconnected sub-graphs.

    :param g: NetworkX graph object
    :param tree: STRTree of all graph nodes
    """
    if nx.is_connected(g):
        return
    else:
        # connect any still disconnected portions
        node_list = np.array(list(g.nodes()))
        main_g = max(nx.connected_components(g), key=len)
        discon_subgs = [
            g.subgraph(c) for c in nx.connected_components(g) if len(c) < len(main_g)
        ]
        target = discon_subgs[0]
        new_edges = []
        invalid_nodes = list(target.nodes())
        starting = invalid_nodes[0]
        dist = 0.005
        increment = 0.005
        valid_targs = []
        while len(valid_targs) < 1:
            valid_targs += [
                n
                for n in node_list[
                    tree.query(starting.location, predicate="dwithin", distance=dist)
                ]
                if n not in invalid_nodes
            ]
            dist += increment
        ending = valid_targs[0]
        new_edges.append(
            Connection(starting, ending, conn_type="street").get_weighted_tuple(
                weighted=True
            )
        )
    g.add_edges_from(new_edges)
    connect_graph(g, tree)
