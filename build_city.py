import pandas as pd

# consider storing all these classes in on file since they are rather compact presently
from rt_network.Station import Station
from rt_network.Connection import Connection
from rt_network.Line import Line
from rt_network.Network import Network

from utils import add_to_db
import pickle
import argparse
from utils import read_city_json
from ast import literal_eval
import numpy as np
from sqlalchemy import create_engine, select, func
import networkx as nx
from tqdm import tqdm

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

passwd = "conductor"  # encrypt somewhere buddy...
engine = create_engine(
    f"postgresql://transitdb_user:{passwd}@localhost/{city}_transitdb"
)

# unpickle metadata object...
filedir = f"data/dbmetadata/{city}db_metadata.pkl"
with open(filedir, "rb") as f:
    transit_metadata = pickle.load(f)

with engine.connect() as conn:
    stations = pd.DataFrame(conn.execute(select(transit_metadata.tables["stations"])))
    station_order = pd.DataFrame(
        conn.execute(select(transit_metadata.tables["station_order"]))
    ).set_index("line")
    rider_data = transit_metadata.tables["rider_data"]
    avg_rides = func.avg(rider_data.c.rides).label("avg_rides")
    query = select(rider_data.c.station_id, avg_rides).group_by(
        rider_data.c.station_id
    )
    daily_boardings = pd.DataFrame(conn.execute(query)).set_index("station_id")

# build network object
# get list of stations
station_set = set()
for stop_id in stations.map_id.unique():
    curr_stop = stations[stations.map_id == stop_id].iloc[0]
    # this order was chosen to mirror the "x/y" coordinate convention typically used in mathematics
    # longitude is thought of as an "x" measurement here and latitude as the "y" measurement
    raw_location = literal_eval(curr_stop.location)
    location = (float(raw_location["longitude"]), float(raw_location["latitude"]))

    line_labels = curr_stop[city_info["lines"]]
    available_lines = line_labels.index[
        np.nonzero(line_labels)
    ]  # all lines a passenger will find at this station
    station_set.add(Station(stop_id, curr_stop.station_name, location, available_lines))

# build lines
# create list of connections for each line
line_objects = set()
for (
    line
) in (
    station_order.index
):  # cant use "lines" here because the lines may have different names
    id_list = station_order.loc[line, "order"]
    connections = set()
    for ind, station_id in enumerate(id_list[:-1]):
        station1 = {
            station for station in station_set if station.network_id == station_id
        }.pop()
        station2 = {
            station for station in station_set if station.network_id == id_list[ind + 1]
        }.pop()
        connections.add(Connection(station1, station2))
    stations_in_line = {station for station in station_set if line in station.lines}
    line_objects.add(Line(stations_in_line, connections, line, weighted=True))

print(f"Generating {city}'s Rapid Transit Network object...")
# generate network connections
transport_network = Network(city, line_objects)
print("Network created.")

# average path length from station * daily boardings (average) / total boardings = weighted trip length measure
def weighted_shortest_path(g, boardings, weight="distance"):
    nodes = list(g)
    index = sorted([node.network_id for node in nodes])
    boardings = boardings[boardings.index.isin(index)]
    total_boardings = float(boardings.avg_rides.sum())

    path_lengths = pd.DataFrame(dict(nx.shortest_path_length(g, weight=weight)))
    path_lengths.index = [i.network_id for i in path_lengths.index]
    path_lengths.columns = [i.network_id for i in path_lengths.columns]
    path_lengths = path_lengths.sort_index().sort_index(axis=1)
    return (
        np.matmul(
            np.diag(boardings.to_numpy().flatten()).astype("float"),
            path_lengths,
        ).sum()
        / total_boardings
    ).mean()

# create a list of all connections that do not exist in graph (between lines only)
print(
    "Fetching weighted average path lengths for all possible new connections..."
)
net_complement = nx.complement(transport_network.graph)
potential_new_connections = [
    edge
    for edge in net_complement.edges
    if len(set(edge[0].lines) & set(edge[1].lines)) == 0
]
# calculate statistics characterizing the network
efficiency_stats = pd.DataFrame(
    index=pd.MultiIndex.from_tuples(potential_new_connections),
    columns=[col for col in transit_metadata.tables["efficiency_stats"].c.keys() if "station" not in col], #removing index stations for later
)
for connection in tqdm(potential_new_connections):
    station1, station2 = connection
    new_conn = Connection(station1, station2) # this is necessary as nx.compliment does not calculate edge distance
    improved_g = transport_network.graph.copy()

    improved_g.add_edge(station1, station2, distance=new_conn.distance)

    # this block feels like there should be a better way but this is the cleanest so far.
    efficiency_stats.loc[connection, "mean_shortest_path_length"] = nx.average_shortest_path_length(improved_g, weight="distance")
    efficiency_stats.loc[connection, "weighted_shortest_path"] = weighted_shortest_path(improved_g, daily_boardings, weight="distance")
    efficiency_stats.loc[connection, "global_efficiency"] = nx.global_efficiency(improved_g)
    efficiency_stats.loc[connection, "barycenter"] = [str(center) for center in nx.barycenter(improved_g, weight="distance")]
    efficiency_stats.loc[connection, "eccentricity"] = [float(i) for i in nx.eccentricity(improved_g, weight="distance").values()]
    efficiency_stats.loc[connection, "avg_clustering"] = nx.average_clustering(improved_g, weight="distance") # potentially more sensible to do this at the node level to detect neighborhoods
    # efficiency_stats.loc[connection, "communicability"] = nx.communicability(improved_g) # This strikes me as detecting redundancy more than anything else
    efficiency_stats.loc[connection, "effective_graph_resistance"] = nx.effective_graph_resistance(improved_g, weight="distance")
    page_dict = nx.pagerank(improved_g, weight="distance")
    efficiency_stats.loc[connection, "pagerank"] = str(dict(zip([str(key) for key in page_dict.keys()], page_dict.values())))
    # efficiency_stats.loc[connection, "smallworld_sigma"] = nx.sigma(improved_g) # these numbers seem off, and it is very slow
    # efficiency_stats.loc[connection, "smallworld_omega"] = nx.omega(improved_g) # I dont think this is a particularly good measure of a transit network

print("Adding network stats to DB...")
efficiency_stats = efficiency_stats.reset_index().rename(columns={"level_0":"station1","level_1":"station2"})
efficiency_stats.loc[:,["station1","station2"]] = efficiency_stats.loc[:,["station1","station2"]].astype(str)
add_to_db("chicago", transit_metadata.tables["efficiency_stats"], engine, source_df=efficiency_stats)
print("Network stats added.")

print("Pickling Network...")
# pickle network object...
directory = f"data/rt_networks/{city}_network.pkl"
output = open(directory, "wb+")
pickle.dump(transport_network, output)
output.close()
print(f"Network pickled and saved at: {directory}")
