import pickle
import argparse

# pass in city
parser = argparse.ArgumentParser(
    prog="RT Network Analyzer", description="Analyzes a city's rapid transit network"
)
parser.add_argument("city_name")
args = parser.parse_args()
city = args.city_name

#unpickle network object...
filedir = f"data/rt_networks/{city}_network.pkl"
with open(filedir, "rb") as f:
    rt_network = pickle.load(f)

#analysis and behavior can be done here
# rt_network.plot_map(
#     optimization_stat="mean_shortest_path_length",
#     asc=True,
#     conn_number=10,
#     style="light",
#     streets=True,
#     bus=True,
#     rail=True,
#     new_conn=True,
# )

# # detect and plot new nodes
from utils import gen_trace
from plotly import graph_objects as go
# from sqlalchemy import select, create_engine
# import pandas as pd
# from tqdm import tqdm
#
# passwd = "conductor"  # encrypt somewhere buddy...
# engine = create_engine(
#     f"postgresql://transitdb_user:{passwd}@localhost/{city}_transitdb"
# )
#
# # unpickle metadata object...
# filedir = f"data/dbmetadata/{city}db_metadata.pkl"
# with open(filedir, "rb") as f:
#     transit_metadata = pickle.load(f)
#
# node_traces = []
# line_traces = []
#
# with engine.connect() as conn:
#     bus_routes = pd.DataFrame(conn.execute(select(transit_metadata.tables["bus_route_shapes"])))
#     bus_stops = pd.DataFrame(conn.execute(select(transit_metadata.tables["bus_stops"])))
#
import shapely as sp
# from rt_network.Node import Node
# from rt_network.Line import Line
# from rt_network.Connection import Connection
#
# bus_stops["available_routes"] = [route.split(",") for route in bus_stops["available_routes"]]
#
# route = "111A"
# mask = [route in row for row in bus_stops.available_routes]
# sample_route = bus_routes[bus_routes.route == route]
# sample_stops = bus_stops[mask]
# sample_route = sp.line_merge(sp.MultiLineString(sample_route["geometry"].iloc[0]["coordinates"]))
# sample_route = sp.LineString([coord for linestring in sample_route.geoms for coord in sorted(linestring.coords)])
# sample_stops = [sp.line_locate_point(sample_route, sp.Point(geom["coordinates"])) for geom in sample_stops["geometry"]]
#
# stop_dists = dict()
# # extract stop order from distance along predefined bus route path
# for stop in sample_stops:
#     stop_dists[stop] = sample_route.interpolate(stop)
#
# stop_order = [
#     Node(
#         net_id=1,
#         name="from_route:public name",
#         location=stop_dists[key].coords[0],
#         lines="from stop: line list",
#         colors="black",
#         node_type="bus"
#     )
#     for key in sorted(stop_dists.keys())
# ]
#
# # build graph for selected route
# route_connections = set()
# route_stops = set()
# for i, stop in enumerate(stop_order[:-1]):
#     route_connections.add(
#         Connection(
#             station1=stop,
#             station2=stop_order[i+1],
#             conn_type="bus"
#         )
#     )
# route_obj = Line(
#     stations = stop_order,
#     connections = route_connections,
#     name = route,
#     color = "black",
#     weighted = True
# )

node_trace = gen_trace(
    "markers",
    1.5,
    "black",
    [node.location for node in rt_network.graph.nodes() if node.node_type == 'bus'])
line_trace = gen_trace("lines",
                       1, "black",
                       sp.MultiLineString([sp.LineString((edge[0].location, edge[1].location))
                                           for edge in rt_network.graph.edges() if (edge[0].node_type == 'bus') and (edge[1].node_type == 'bus')]))

fig = go.Figure(layout=go.Layout(map=dict(center=({'lat':41.88152, 'lon':-87.68218}), zoom=10,)))
fig.add_trace(node_trace)
fig.add_trace(line_trace)
fig.show()