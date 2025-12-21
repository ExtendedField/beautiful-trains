###
# creates city network object using station locations as well as train a bus line geometries. Additionally, extracts
# the impact of new connections on network summary statistics in order to recommend most impactful new connections.
###

#TODO: this file needs to be simplified by removing redundancy and repackaging certain parts into cleanly named functions

import pandas as pd

# consider storing all these classes in on file since they are rather compact presently
from city_network.network_components import Connection, Node, Line
from city_network.network import Network
from plotting import utils

from utils import connect_closest
from collect_data.utils import add_to_db, read_city_json
import pickle
import argparse
import numpy as np
from sqlalchemy import create_engine, select, func
import networkx as nx
from tqdm import tqdm
from shapely import (
    MultiLineString,
    Point,
)

# pass in city
parser = argparse.ArgumentParser(
    prog="RT Network Generator",
    description="Generates network structure for a city's rapid transit network",
)
parser.add_argument("city_name")
parser.add_argument("-r", "--refresh", action="store_true")
parser.add_argument("--nodata", action="store_true")
args = parser.parse_args()
city = args.city_name
refresh = args.refresh
include_data = not args.nodata

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
    train_stations_db = transit_metadata.tables["train_stations"]
    line_aggs = []
    for line in city_info["lines"].keys():
        line_aggs.append(func.bool_or(train_stations_db.c[line]).label(line))
    location_func = func.array_agg(train_stations_db.c.location)[1].label("location")
    query = select(
        train_stations_db.c["station_name", "map_id"], location_func, *line_aggs
    ).group_by(train_stations_db.c["station_name", "map_id"])
    train_stations = pd.DataFrame(conn.execute(query))
    station_order = pd.DataFrame(
        conn.execute(select(transit_metadata.tables["train_station_order"]))
    ).set_index("line")
    rider_data = transit_metadata.tables["rider_data"]
    avg_rides = func.avg(rider_data.c.rides).label("avg_rides")
    query = select(rider_data.c.station_id, avg_rides).group_by(rider_data.c.station_id)
    daily_rail_boardings = pd.DataFrame(conn.execute(query)).set_index("station_id")
    train_line_shapes = pd.DataFrame(
        conn.execute(select(transit_metadata.tables["train_line_shapes"]))
    )
    bus_route_shapes = pd.DataFrame(
        conn.execute(select(transit_metadata.tables["bus_route_shapes"]))
    )
    bus_stops = pd.DataFrame(conn.execute(select(transit_metadata.tables["bus_stops"])))
    streets = pd.DataFrame(conn.execute(select(transit_metadata.tables["streets"])))

node_set = set()
line_objects = set()
# build network object
# rail
for stop_id in train_stations.map_id.unique():
    curr_stop = train_stations[train_stations.map_id == stop_id].iloc[0]
    raw_location = curr_stop.location
    # the below order was chosen to mirror the "x/y" coordinate convention typically used in mathematics
    # longitude is thought of as an "x" measurement here and latitude as the "y" measurement
    location = (float(raw_location["longitude"]), float(raw_location["latitude"]))
    line_labels = curr_stop[city_info["lines"].keys()].T
    available_lines = line_labels.index[
        np.nonzero(line_labels)
    ]  # all lines a passenger will find at this station
    colors = [
        city_info["lines"][line]
        for line in city_info["lines"].keys()
        if line in available_lines
    ]
    node_set.add(
        Node(
            stop_id,
            curr_stop.station_name,
            location,
            available_lines,
            colors,
            node_type="rail",
        )
    )
# bus stops
bus_stops.loc[:, "available_routes"] = [
    route_str.split(",") for route_str in bus_stops.available_routes
]
routes = {route for route_lst in bus_stops.available_routes for route in route_lst}
# removes extraneous lines. mostly due to data inconsistencies. chicago only has 2 mislabeled lines
valid_routes = set(bus_route_shapes.route).intersection(routes)

# detects bus routes
for route in tqdm(valid_routes, desc="Detecting bus routes"):
    # this logic should be abstracted and used for rail lines as well.
    curr_route = bus_route_shapes[bus_route_shapes.route == route]
    mask = [route in row for row in bus_stops.available_routes]
    curr_stops = bus_stops[mask]
    curr_route = MultiLineString(curr_route["geometry"].iloc[0]["coordinates"])

    # determine which subline points correspond to
    # projection does not place point exactly on the line. 'tolerance' can be tweaked to adjust
    tolerance = 0.0000001
    sublines = dict()
    for line in curr_route.geoms:
        sublines[line] = []
        for i, stop in curr_stops.iterrows():
            point = stop.geometry["coordinates"]
            if (
                curr_route.interpolate(curr_route.project(Point(point)))
                .buffer(tolerance)
                .intersects(line)
            ):
                sublines[line].append(stop)

    route_connections = set()
    route_stops = set()
    end_points = dict()
    subline_id = 0
    num_loops = 0
    for line in sublines.keys():
        order = sorted(
            [
                (  # tuple order is important because sorted by default uses the first tuple value
                    utils.project(Point(stop.geometry["coordinates"])),
                    Node(
                        net_id=stop.system_stop,
                        name=stop.public_name,
                        location=Point(stop.geometry["coordinates"]),
                        lines=stop.available_routes,
                        colors="black",
                        node_type="bus",
                    ),
                )
                for stop in sublines[line]
            ],
            key=lambda node: node[0],
        )
        if len(order) > 0:
            first = order[0][1]
            last = order[-1][1]
            is_loop = (first == last) and (len(order) > 1)
            if is_loop:
                print(order)
            end_points[first] = {"id": subline_id, "loop": is_loop}
            end_points[last] = {"id": subline_id, "loop": is_loop}
            subline_id += 1
            route_stops = route_stops.union(set(order))
            for i, item in enumerate(order[:-1]):
                route_connections.add(
                    Connection(
                        station1=item[1], station2=order[i + 1][1], conn_type="bus"
                    )
                )
    connect_closest(end_points, route_connections)
    line_objects.add(
        Line(
            stations=route_stops,
            connections=route_connections,
            name=route,
            color="black",
            weighted=True,
        )
    )

# build rail lines
# create list of connections for each line
for (
    line
) in (
    station_order.index
):  # cant use "lines" here because the lines may have different names
    id_list = station_order.loc[line, "order"]
    # generate connections potentially by using trace data and coord lists?
    connections = set()
    for ind, station_id in enumerate(id_list[:-1]):
        station1 = {
            station for station in node_set if station.network_id == station_id
        }.pop()
        station2 = {
            station for station in node_set if station.network_id == id_list[ind + 1]
        }.pop()
        connections.add(Connection(station1, station2))
    stations_in_line = {
        station for station in node_set if any([lyne in line for lyne in station.lines])
    }
    # resolves multiple endpoint issue
    true_line = [l for l in city_info["lines"].keys() if l in line][0]
    line_color = city_info["lines"][true_line]
    line_objects.add(
        Line(
            stations_in_line,
            connections,
            line,
            line_color,
            weighted=True,
            line_type="rail",
        )
    )

print(f"Generating {city}'s Rapid Transit Network object...")
# generate network connections
transport_network = Network(
    city,
    line_objects,
    rail_shapes=train_line_shapes,
    bus_route_shapes=bus_route_shapes,
    street_shapes=streets,
)
print("Network created.")

# TODO: find a way to analyze impact of changing the travel resistance of connections on graph summary stats.
if include_data:
    from utils import weighted_shortest_path
    from itertools import product

    # create a list of all connections that do not exist in graph (between lines only)
    print("Fetching summary stats for all possible new connections...")
    conn_lists = dict()
    for node_type in transport_network.available_modes:
        conn_lists[node_type] = [
            node for node in transport_network.nodes if node.node_type == node_type
        ]
    # streets direct to rail connections, rail to rail might be exhaustive for this approach.
    street_to_rail = [
        Connection(st1, st2, conn_type="rail").get_weighted_tuple(weighted=True)
        for st1, st2 in tqdm(
            product(conn_lists["street"], conn_lists["rail"]),
            desc="Generating new potential connections from street to rail",
        )
    ]
    rail_to_rail = [
        Connection(st1, st2, conn_type="rail").get_weighted_tuple(weighted=True)
        for st1, st2 in tqdm(
            product(conn_lists["rail"], conn_lists["rail"]),
            desc="Generating new potential connections from rail to rail",
        )
        if len(set(st1.lines).intersection(set(st2.lines))) == 0
    ]

    potential_new_connections = rail_to_rail + street_to_rail
    # calculate statistics characterizing the network
    efficiency_stats = pd.DataFrame(
        index=pd.MultiIndex.from_tuples(
            [(conn[0], conn[1]) for conn in potential_new_connections]
        ),
        columns=[
            col
            for col in transit_metadata.tables["efficiency_stats"].c.keys()
            if "node" not in col
        ],  # removing index nodes for later
    )
    # research kubernetes and think about how to smartly pair down the sample size.
    for connection in tqdm(
        potential_new_connections[:5],
        desc="Generating efficiency stats for all potential new connections",
    ):
        node1, node2, meta_data = connection
        improved_g = transport_network.graph.copy()
        improved_g.add_edge(
            node1, node2, travel_resistance=meta_data["travel_resistance"]
        )

        weight = "travel_resistance"
        # this block feels like there should be a better way but this is the cleanest so far.
        efficiency_stats.loc[connection, "mean_shortest_path_length"] = (
            nx.average_shortest_path_length(improved_g, weight=weight)
        )
        efficiency_stats.loc[connection, "weighted_shortest_path"] = (
            weighted_shortest_path(improved_g, daily_rail_boardings, weight=weight)
        )
        efficiency_stats.loc[connection, "global_efficiency"] = nx.global_efficiency(
            improved_g
        )
        efficiency_stats.loc[connection, "barycenter"] = [
            str(center) for center in nx.barycenter(improved_g, weight=weight)
        ]
        efficiency_stats.loc[connection, "eccentricity"] = [
            float(i) for i in nx.eccentricity(improved_g, weight=weight).values()
        ]
        efficiency_stats.loc[connection, "avg_clustering"] = nx.average_clustering(
            improved_g, weight=weight
        )  # potentially more sensible to do this at the node level to detect neighborhoods
        efficiency_stats.loc[connection, "effective_graph_resistance"] = (
            nx.effective_graph_resistance(improved_g, weight=weight)
        )
        page_dict = nx.pagerank(improved_g, weight=weight)
        efficiency_stats.loc[connection, "pagerank"] = str(
            dict(zip([str(key) for key in page_dict.keys()], page_dict.values()))
        )

    print("Adding network stats to DB...")
    efficiency_stats = efficiency_stats.reset_index().rename(
        columns={"level_0": "node1", "level_1": "node2"}
    )
    efficiency_stats.loc[:, ["node1", "node2"]] = efficiency_stats.loc[
        :, ["node1", "node2"]
    ].astype(str)
    add_to_db(
        "chicago",
        transit_metadata.tables["efficiency_stats"],
        engine,
        source_df=efficiency_stats,
    )
    print("Network stats added.")

print("Pickling Network...")
directory = f"data/rt_networks/{city}_network.pkl"
output = open(directory, "wb+")
pickle.dump(transport_network, output)
output.close()
print(f"Network pickled and saved at: {directory}")
