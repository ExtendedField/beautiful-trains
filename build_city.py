# consider storing all these classes in on file since they are rather compact presently
from rt_network.Station import Station
from rt_network.Connection import Connection
from rt_network.Line import Line
from rt_network.Network import Network
from data.schemas import schemas

import pickle
import argparse
from utils import add_to_db, read_city_json, build_table
from ast import literal_eval
import numpy as np
from sqlalchemy import (
    create_engine,
    MetaData,
)
from pprint import pprint

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
table_info = city_info["tables"]
# below block will expand as new apis are added
if city_info["client_api"] == "socrata":
    from sodapy import Socrata
    client = Socrata(city_info["website"], city_info["token"])
else:
    raise Exception("Unknown client id. Please try another")

# create and load data into Postgre database
import subprocess

# shell script creates the db with the name "{city}_transitdb" if it does not
# already exist. It also creates a user role called "transitdb_user" if it
# does not already exist
subprocess.run(["sh", "./setupdb.sh", city])

transit_metadata = MetaData()
passwd = "conductor" # encrypt somewhere buddy...
engine = create_engine(
    f"postgresql://transitdb_user:{passwd}@localhost/{city}_transitdb"
)

tables = [build_table(transit_metadata, table_name, schema) for table_name, schema in schemas.items()]
transit_metadata.create_all(engine)
for table in tables:
    table_id = city_info["tables"][table.name]["remote_table_id"]
    local_dir = city_info["tables"][table.name]["local_dir"]
    add_to_db(city, table, engine, client, table_id=table_id, source_csv=local_dir)

station_id_map = station_id_map.groupby(level=0).agg(group_funcs)
station_id_map[city_info["lines"]] = station_id_map[city_info["lines"]].astype(bool)

# build network object
# get list of stations
stations = set()
for stop in station_id_map.index.unique():
    curr_stop = stations_raw[stations_raw["station_descriptive_name"] == stop].iloc[0]
    net_id = int(station_id_map.loc[stop, "station_id"])
    # this order was chose to mirror the "x/y" coordinate convention typically used in mathematics
    # longitude is thought of as an "x" measurement here and latitude as the "y" measurement
    raw_location = literal_eval(curr_stop.location)
    location = (float(raw_location["longitude"]), float(raw_location["latitude"]))

    line_labels = curr_stop[city_info["lines"]]
    available_lines = line_labels.index[
        np.nonzero(line_labels)
    ]  # all lines a passenger will find at this station
    stations.add(Station(net_id, stop, location, available_lines))

# build lines
# create list of connections for each line
line_objects = set()
for (
    line
) in (
    station_order.columns
):  # cant use "lines" here because the lines may have different names
    id_list = [iden for iden in list(station_order.T.loc[line]) if str(iden) != "nan"]
    connections = set()
    for ind, station_id in enumerate(id_list[:-1]):
        station1 = {
            station for station in stations if station.network_id == station_id
        }.pop()
        station2 = {
            station for station in stations if station.network_id == id_list[ind + 1]
        }.pop()
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
