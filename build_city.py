# consider storing all these classes in on file since they are rather compact presently
import pandas as pd

from rt_network.Station import Station
from rt_network.Connection import Connection
from rt_network.Line import Line
from rt_network.Network import Network

import pickle
import argparse
from utils import read_city_json
from ast import literal_eval
import numpy as np
from sqlalchemy import create_engine, select

# pass in city
parser = argparse.ArgumentParser(
    prog="RT Network Generator",
    description="Generates network structure for a city's rapid transit network",
)
parser.add_argument("city_name")
parser.add_argument("-r", "--refresh", type=bool)
args = parser.parse_args()
city = args.city_name
refresh = args.refresh

city_info = read_city_json(city, "./data/city_info.json")

passwd = "conductor" # encrypt somewhere buddy...
engine = create_engine(
    f"postgresql://transitdb_user:{passwd}@localhost/{city}_transitdb"
)

# unpickle metadata object...
filedir = f"data/dbmetadata/{city}db_metadata.pkl"
with open(filedir, "rb") as f:
    transit_metadata = pickle.load(f)

with engine.connect() as conn:
    stations = pd.DataFrame(conn.execute(select(transit_metadata.tables["stations"])))
    station_order = pd.DataFrame(conn.execute(select(transit_metadata.tables["station_order"])))

# # build network object
# # get list of stations
# station_set = set()
# for stop in stations:
#     curr_stop = stations[stations["station_descriptive_name"] == stop].iloc[0]
#     net_id = stations.map_id
#     # this order was chose to mirror the "x/y" coordinate convention typically used in mathematics
#     # longitude is thought of as an "x" measurement here and latitude as the "y" measurement
#     raw_location = literal_eval(curr_stop.location)
#     location = (float(raw_location["longitude"]), float(raw_location["latitude"]))
#
#     line_labels = curr_stop[city_info["lines"]]
#     available_lines = line_labels.index[
#         np.nonzero(line_labels)
#     ]  # all lines a passenger will find at this station
#     station_set.add(Station(net_id, stop, location, available_lines))
#
# # build lines
# # create list of connections for each line
# line_objects = set()
# for (
#     line
# ) in (
#     station_order.columns
# ):  # cant use "lines" here because the lines may have different names
#     id_list = [iden for iden in list(station_order.T.loc[line]) if str(iden) != "nan"]
#     connections = set()
#     for ind, station_id in enumerate(id_list[:-1]):
#         station1 = {
#             station for station in stations if station.network_id == station_id
#         }.pop()
#         station2 = {
#             station for station in stations if station.network_id == id_list[ind + 1]
#         }.pop()
#         connections.add(Connection(station1, station2))
#     stations_in_line = {station for station in stations if line in station.lines}
#     line_objects.add(Line(stations_in_line, connections, weighted=True))
#
# print(f"Generating {city}'s Rapid Transit Network object...")
# # generate network connections
# transport_network = Network(city, line_objects)
# print("Network created.")
#
# print("Pickling Network...")
# # pickle network object...
# directory = f"data/rt_networks/{city}_network.pkl"
# output = open(directory, "wb+")
# pickle.dump(transport_network, output)
# output.close()
# print(f"Network pickled and saved at: {directory}")
