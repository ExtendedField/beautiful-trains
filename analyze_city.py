import pprint, pickle
import argparse

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

# pprint.pprint(rt_network.graph.nodes)

rt_network.plot()