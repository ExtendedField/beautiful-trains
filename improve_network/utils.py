import networkx as nx
import numpy as np
import pandas as pd


def weighted_shortest_path(g, boardings, weight="travel_resistance"):
    """
    Calculates the average shortest path between network nodes weighted by daily boardings at the node.

    :param g: NetworkX graph object
    :param boardings: DataFrame of daily boardings at each station
    :param weight: the edge attribute by which to weight.
    :returns: mean-weighted-shortest-path length
    """
    # average path length from station * daily boardings (average) / total boardings = weighted trip length measure
    nodes = list(g)
    index = sorted([node.network_id for node in nodes])
    boardings = boardings[boardings.index.isin(index)]
    total_boardings = float(boardings.avg_rides.sum())

    path_lengths = pd.DataFrame(dict(nx.shortest_path_length(g, weight=weight)))
    path_lengths.index = [i.network_id for i in path_lengths.index]
    path_lengths.columns = [i.network_id for i in path_lengths.columns]
    path_lengths = path_lengths.sort_index().sort_index(axis=1)
    return (
        np.matmul(
            np.diag(boardings.to_numpy().flatten()).astype("float"),
            path_lengths,
        ).sum()
        / total_boardings
    ).mean()
