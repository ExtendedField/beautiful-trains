# consider storing all these classes in on file since they are rather compact presently
from rt_network.Station import Station
from rt_network.Connection import Connection
from rt_network.Line import Line
from rt_network.Network import Network

import pickle
import argparse
from rt_network.utils import get_data, read_city_json
from ast import literal_eval
import numpy as np

# pass in city
parser = argparse.ArgumentParser(prog='RT Network Generator',
                                 description="Generates network structure for a city's rapid transit network")
parser.add_argument("city_name")
parser.add_argument("-r", "--refresh", type=bool)
args = parser.parse_args()
city = args.city_name
refresh = args.refresh

# fetch relevant data
stations_raw = get_data(city, "stations")
station_id_map = get_data(city, "station_id_map").set_index("station_descriptive_name").drop(columns=["station_name"])
station_order = get_data(city, "station_order")
lines = read_city_json(city, "./data/city_info.json")["lines"]

# pre-process id mapping
# below removes duplicate rows by flattening instances where different directions have different lines present
# into one list of all lines available at the station. Also removes duplicate IDs by defaulting to the maximum id value
group_funcs = {}
for col in station_id_map.columns:
    if col == "station_id":
        group_funcs[col] = "max"
    else:
        group_funcs[col] = "sum"

station_id_map = station_id_map.groupby(level=0).agg(group_funcs)
station_id_map[lines] = station_id_map[lines].astype(bool)

# build network object
# get list of stations
stations = set()
for stop in station_id_map.index.unique():
    curr_stop = stations_raw[stations_raw["station_descriptive_name"] == stop].iloc[0]
    net_id = int(station_id_map.loc[stop,"station_id"])
    # this order was chose to mirror the "x/y" coordinate convention typically used in mathematics
    # longitude is thought of as an "x" measurement here and latitude as the "y" measurement
    raw_location = literal_eval(curr_stop.location)
    location = (float(raw_location['longitude']), float(raw_location['latitude']))

    line_labels = curr_stop[lines]
    available_lines = line_labels.index[np.nonzero(line_labels)]  # all lines a passenger will find at this station
    stations.add(Station(net_id, stop, location, available_lines))

# build lines
# create list of connections for each line
line_objects = set()
for line in station_order.columns: # cant use "lines" here because the lines may have different names
    id_list = [iden for iden in list(station_order.T.loc[line]) if str(iden) != "nan"]
    connections = set()
    for ind, station_id in enumerate(id_list[:-1]):
        station1 = {station for station in stations if station.network_id == station_id}.pop()
        station2 = {station for station in stations if station.network_id == id_list[ind+1]}.pop()
        connections.add(Connection(station1, station2))
    stations_in_line = {station for station in stations if line in station.lines}
    line_objects.add(Line(stations_in_line, connections, weighted=True))

print(f"Generating {city}'s Rapid Transit Network object...")
# generate network connections
transport_network = Network(city, line_objects)
print("Network created.")

print("Pickling Network...")
# pickle network object...
directory = f"data/rt_networks/{city}_network.pkl"
output = open(directory, "wb+")
pickle.dump(transport_network, output)
output.close()
print(f"Network pickled and saved at: {directory}")
