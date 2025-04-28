import pickle
import argparse

# import networkx as nx
import pandas as pd

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

print("\nCurrent rail network summary stats:")
print(f"Clustering Coefficient: {rt_network.glob_cluster_coef}")
print(f"Average Path Length: {rt_network.avg_path_len}")
print(f"Degree Distribution: {rt_network.degree_dist}\n")

# daily_rail_boardings = pd.read_csv("~/project_repos/beautiful-trains/data/rail_station_orders/pt_rider_data.csv")
# avg_boardings = daily_rail_boardings[["station_id", "stationname", "rides"]].groupby(by=["station_id", "stationname"]).mean()
# print(avg_boardings.head(50))

# rt_network.plot()

print(
    rt_network.potential_connections.sort_values(
        by="avg_path_length", ascending=True
    ).head(25)
)  # .connection_name.values)

# suggestions often overlap with existing lines. This suggests the network may benefit from express trains
# one potential solution is to ignore new connections with a high overlap with existing ones.
# this could be measured wby plotting the stations as points on a grid, and then measuring the correlations of the lines corresponding
# to new connections with the existing stations, to select for more net new connections.
