###
# script used for analyzing the network object to do things like plot the network shape or graph primitive or
# report specific summary stats about the network.
###

import pickle
import argparse

import networkx as nx

# pass in city
parser = argparse.ArgumentParser(
    prog="RT Network Analyzer", description="Analyzes a city's rapid transit network"
)
parser.add_argument("city_name")
args = parser.parse_args()
city = args.city_name

# unpickle network object...
filedir = f"data/rt_networks/{city}_network.pkl"
with open(filedir, "rb") as f:
    rt_network = pickle.load(f)

# analysis and behavior can be done here
# city_network.plot_map(
#     optimization_stat="mean_shortest_path_length",
#     asc=True,
#     conn_number=10,
#     style="light",
#     streets=True,
#     bus=True,
#     rail=True,
#     #new_conn=True,
#     graph_view=True
# )
print([c.travel_resistance for c in rt_network.connections][0])
print([len(c) for c in nx.connected_components(rt_network.graph)])
