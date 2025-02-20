import pickle
import argparse

import networkx as nx

# pass in city
parser = argparse.ArgumentParser(prog='RT Network Analyzer',
                                 description="Analyzes a city's rapid transit network")
parser.add_argument("city_name")
args = parser.parse_args()
city = args.city_name

# unpickle network object...
filedir = f"data/rt_networks/{city}_network.pkl"
with open(filedir, 'rb') as f:
    rt_network = pickle.load(f)

# print(nx.get_edge_attributes(rt_network.graph, "weight"))
# pprint.pprint([edge for edge in rt_network.graph.edges])

#TODO: Implement showing network efficiency and then probably transfer into the class
g = rt_network.graph
cluster_coef = nx.clustering(g)
avg_path = nx.average_shortest_path_length(g)
degree_dist = nx.degree_histogram(g)

print(f"Clustering Coefficient: {cluster_coef}")
print(f"Average Path Length: {avg_path}")
print(f"Degree Distribution: {degree_dist}")

# rt_network.plot()