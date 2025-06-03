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
    bus_data = pd.DataFrame(conn.execute(select(transit_metadata.tables["bus_route_shapes"])))

import geopandas as gpd
from shapely import MultiLineString
import momepy as mp

bus_data.loc[:,"geometry"] = [MultiLineString(item["coordinates"]) for item in bus_data.loc[:,"geometry"]]
bus_data = gpd.GeoDataFrame(bus_data, geometry="geometry").explode()
g = mp.gdf_to_nx(bus_data)

node_trace = gen_trace("markers", 1.5, "black", g.nodes())
line_trace = gen_trace("lines", 1, "black", g.edges())

fig = go.Figure()
fig.add_trace(node_trace)
fig.add_trace(line_trace)
fig.show()