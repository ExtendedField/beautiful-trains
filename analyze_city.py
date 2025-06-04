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

# detect and plot new nodes
from utils import gen_trace
from plotly import graph_objects as go
from sqlalchemy import select, create_engine
import pandas as pd
from tqdm import tqdm

passwd = "conductor"  # encrypt somewhere buddy...
engine = create_engine(
    f"postgresql://transitdb_user:{passwd}@localhost/{city}_transitdb"
)

# unpickle metadata object...
filedir = f"data/dbmetadata/{city}db_metadata.pkl"
with open(filedir, "rb") as f:
    transit_metadata = pickle.load(f)

node_traces = []
line_traces = []

with engine.connect() as conn:
    bus_routes = pd.DataFrame(conn.execute(select(transit_metadata.tables["bus_route_shapes"])))
    bus_stops = pd.DataFrame(conn.execute(select(transit_metadata.tables["bus_stops"])))

import shapely as sp

bus_stops["available_routes"] = [route.split(",") for route in bus_stops["available_routes"]]

route = "76"
mask = [route in row for row in bus_stops.available_routes]
sample_route = bus_routes[bus_routes.route == route]
sample_stops = bus_stops[mask]
sample_route = sp.MultiLineString(sample_route["geometry"].iloc[0]["coordinates"])
sample_stops = [sample_route.interpolate(sample_route.project(sp.Point(geom["coordinates"]))) for geom in sample_stops["geometry"]]

node_trace = gen_trace("markers", 1.5, "black", sample_stops)
line_trace = gen_trace("lines", 1, "black", sample_route)

fig = go.Figure()
fig.add_trace(node_trace)
fig.add_trace(line_trace)
fig.show()