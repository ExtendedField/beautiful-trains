import pprint, pickle
import argparse

# pass in city
parser = argparse.ArgumentParser(prog='RT Network Analyzer',
                                 description="Analyzes a city's rapid transit network")
parser.add_argument("city_name")
args = parser.parse_args()
city = args.city_name

# unpickle network object...
pkl_network = open(f"data/rt_networks/{city}_network.pkl", "wb+")

unpkl_network = pickle.load(pkl_network)
pprint.pprint(unpkl_network)

pkl_network.close()
