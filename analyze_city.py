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
from sqlalchemy import create_engine

passwd = "conductor"  # encrypt somewhere buddy...
engine = create_engine(
    f"postgresql://transitdb_user:{passwd}@localhost/{city}_transitdb"
)
from shapely import LineString, MultiLineString

# unpickle metadata object...
filedir = f"data/dbmetadata/{city}db_metadata.pkl"
with open(filedir, "rb") as f:
    transit_metadata = pickle.load(f)

node_traces = []
line_traces = []

node_trace = gen_trace(
    "markers",
    1.5,
    "black",
    [node.location for node in rt_network.graph.nodes() if node.node_type == 'bus']
)
line_trace = gen_trace(
    "lines",
    1,
    "black",
    MultiLineString(
        [
            LineString((edge[0].location, edge[1].location))
            for edge in rt_network.graph.edges()
            if (edge[0].node_type == 'bus') and (edge[1].node_type == 'bus')
        ]
    )
)

fig = go.Figure(layout=go.Layout(map=dict(center=({'lat':41.88152, 'lon':-87.68218}), zoom=10,)))
fig.add_trace(node_trace)
fig.add_trace(line_trace)
fig.show()