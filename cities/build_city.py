from rt_network.Network import Network
from rt_network.Station import Station
from rt_network.Connection import Connection
import argparse
from data.utils import get_data, read_city_json
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
rt_network_data = get_data(city, "rt_stops")
lines = read_city_json(city, "./city_data_locations.json")["lines"]

# build network object
# get list of stations
stations = []
for stop in rt_network_data["station_name"].unique():
    curr_stop = rt_network_data[rt_network_data["station_name"] == stop].iloc[0]
    net_id = curr_stop.stop_id
    # this order was chose to mirror the "x/y" coordinate convention typically used in mathematics
    # longitude is thought of as an "x" measurement here and latitude as the "y" measurement
    raw_location = literal_eval(curr_stop.location)
    location = (float(raw_location['longitude']), float(raw_location['latitude']))

    line_labels = curr_stop[lines]
    available_lines = line_labels.index[np.nonzero(line_labels)]  # all lines a passenger will find at this station

    stations.append(Station(net_id, stop, location, available_lines))

# generate connections
connections = []
for station in stations:
    connecting_stations = [potential_connection for potential_connection in stations if station.connects(potential_connection)]
    connections.append(connection)


# store network object...

