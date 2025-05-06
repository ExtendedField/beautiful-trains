import pickle
import argparse

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

# analysis and behavior can be done here
rt_network.plot(show_new_conn=True)
