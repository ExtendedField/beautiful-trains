###
# script used for analyzing the network object to do things like plot the network shape or graph primitive or
# report specific summary stats about the network.
###
import pandas as pd
# import pickle
# import argparse
#
# import networkx as nx
#
# # pass in city
# parser = argparse.ArgumentParser(
#     prog="RT Network Analyzer", description="Analyzes a city's rapid transit network"
# )
# parser.add_argument("city_name")
# args = parser.parse_args()
# city = args.city_name
#
# # unpickle network object...
# filedir = f"data/rt_networks/{city}_network.pkl"
# with open(filedir, "rb") as f:
#     rt_network = pickle.load(f)

####
# 1. read in data from OpenStreetMaps using OSMnx -> NetworkX graph
# 2. shape network data for pandana
# 3. create pdna network from NetworkX network
# 4. develop fast way of calculating either sampled or true mean travel time
####
# We also want to think about other ways the query could be useful. OSM or other may be able to assign
# populations to each node making it possible to do population weighted analysis like measuring how many people
# are unserviced. Or measuring the incomes of unserviced people. Potentially finding isolated subcommunities
# and plotting to see which are unconnected is now possible. Or getting regional population weighted access to rail.
####

####
# Notes: plotting not as good as mine. Probably keep that functionality if possible
####

import osmnx as ox
import pandana as pdna
from tqdm import tqdm
from pandana.loaders import osm
import random


nx_network = ox.graph.graph_from_place(
    'Eugene, Oregon, USA',
    network_type='all_public',
    simplify=True,
    retain_all=True,
)
nx_network = ox.routing.add_edge_speeds(nx_network)
nx_network = ox.routing.add_edge_travel_times(nx_network)

def nx_to_pdna(G):
    """
    Converts NetworkX graph object to a pandana network object

    :param G: NetworkX graph object
    :returns: pandana network object
    """
    json_formatted_nodes = pd.DataFrame(G.nodes(data=True)).set_index(0)
    nodes = pd.json_normalize(json_formatted_nodes[1])
    nodes.index = json_formatted_nodes.index

    json_formatted_edges = pd.DataFrame(G.edges(data=True)).set_index([0,1])
    edges = pd.json_normalize(json_formatted_edges[2])
    edges.index = json_formatted_edges.index
    edges = edges.reset_index().rename(columns={0:"from", 1:"to"})

    net = pdna.Network(nodes["x"], nodes["y"], edges["from"], edges["to"], edges[["travel_time"]])

    return net

pdna_net = nx_to_pdna(nx_network)
pdna_net.precompute(3600) # I think this number is in seconds but we may want to verify

def pdna_mean_shortest_path(pdna_network, sample_size=None):
    """
    Calculates the mean shortest path of a pdan_network

    :param pdna_network: network object from pandana library
    :param sample_size: limit number of connections to be considered for memory reasons.
    :returns: float corresponding to the mean shortest path of the network
    """
    from itertools import product
    import time

    if sample_size is None:
        nodes = list(pdna_network.node_ids)
    else:
        nodes = list(pdna_network.node_ids)[:sample_size]
    node_permutations = product(nodes, nodes)

    print("Removing duplicates")
    start = time.time()
    node_combinations = set(tuple(sorted(perm)) for perm in node_permutations)
    end = time.time()
    print(f"Duplicate removal time {end-start}")

    print("separating into starts and ends")
    start = time.time()
    starts , ends = zip(*node_combinations)
    end = time.time()
    print(f"Unzipping time {end-start}")

    print("calculating path lengths")
    start = time.time()
    path_durations = pdna_network.shortest_path_lengths(
        starts,
        ends,
        #imp_name="travel_time"
    )
    end = time.time()
    print(f"Path length calculation time {end-start}")

    return sum(path_durations)/len(path_durations)


# starts = pd.Series(net.node_ids).loc[random.sample(range(num_nodes), 1000)]
# ends = pd.Series(net.node_ids).loc[random.sample(range(num_nodes), 1000)]
# path_lens = net.shortest_path_lengths(starts, ends)


print(f"Number of total nodes: {len(pdna_net.node_ids)}")
# print(f"Number of dists calculated: {len(shortest_lengths)}")
print(f"Average path length of network: {pdna_mean_shortest_path(pdna_net, sample_size=3000)}")

# G = ox.graph.graph_from_place("Eugene, Oregon, USA", network_type="all_public")
# G = ox.routing.add_edge_speeds(G)
# G = ox.routing.add_edge_travel_times(G)
# nodes = pd.DataFrame(columns=["x","y"])
# edges = pd.DataFrame(columns=["from", "to", "weight"])
# for node in tqdm(G.nodes(data=True)):
#     nodes.loc[node[0], "x"] = node[1]["x"]
#     nodes.loc[node[0], "y"] = node[1]["y"]
#
# for edge in tqdm(G.edges(data=True)):
#     new_row = pd.DataFrame(
#         {
#             "from": [edge[0]],
#             "to": [edge[1]],
#             "weight":[edge[2]["travel_time"]]
#         }
#     )
#     edges = pd.concat([edges, new_row], ignore_index=True)
#
# print(nodes.head(3))
# print(edges.head(3))
#
# # net=pdna.Network(nodes["x"], nodes["y"], edges["from"], edges["to"], edges[["weight"]])
# net.precompute(3000)