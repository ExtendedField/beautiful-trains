import plotly
from city_network.network import Network


def plot_network_graph(transit_network: Network) -> None:
    pass


def plot_network_street_shapes(transit_network: Network) -> None:
    pass


### Legacy use for refactor/rework above
# TODO: implement a voronoi cell plotting function once all nodes are added
# TODO: change to something like: plot_graph or plot_map functions. Decide about subdividing for each layer, and
#       if there is a clean way to add supporting functions to avoid repeating code.
def plot_map(
    self,
    new_conn=False,
    optimization_stat="mean_shortest_path_length",
    asc=True,
    conn_number=10,
    style="light",
    rail=True,
    bus=True,
    streets=True,
    graph_view=False,
) -> None:
    """
    A function to plot a cities rapid transit network as an image, optionally adding in recommended new
    connections.

    :param new_conn: boolean indicating to plot recommended network improvements
    :param optimization_stat: what network statistic should be used to determine the best new connections
    :param asc: true if 'lower is better' for the passed statistic. False if 'higher is better'
    :param conn_number: number of new connections to plot
    :param style: map style to be used by pyplot
    :param rail: boolean indicating to plot rail connections
    :param bus: boolean indicating to plot bus lines
    :param streets: boolean indicating to plot city streets
    :param graph_view: True to plot graph primitive, False to plot physical geometries
    """
    # reference link: https://plotly.com/python/network-graphs/
    import plotly.graph_objects as go
    from sqlalchemy import create_engine, select
    import pickle
    import pandas as pd
    from plotting.utils import gen_graph_geoms
    from plotting.utils import gen_trace
    from shapely import MultiLineString
    from networkx import barycenter, subgraph

    passwd = "conductor"  # encrypt somewhere buddy...
    engine = create_engine(
        f"postgresql://transitdb_user:{passwd}@localhost/{self.city}_transitdb"
    )

    # unpickle metadata object...
    filedir = f"data/dbmetadata/{self.city}db_metadata.pkl"
    with open(filedir, "rb") as f:
        transit_metadata = pickle.load(f)

    node_traces = []
    line_traces = []

    with engine.connect() as conn:
        if streets:
            streets_data = pd.DataFrame(
                conn.execute(select(transit_metadata.tables["streets"]))
            )
            if graph_view:
                street_geoms = gen_graph_geoms(self.graph, "street")
            else:
                street_geoms = MultiLineString(
                    [
                        MultiLineString(segment["coordinates"])
                        for segment in streets_data.geometry
                    ]
                )
            line_traces.append(gen_trace("lines", 0.5, "grey", street_geoms))
            street_corners = [node.location for node in self.nodes_by_type["street"]]
            node_traces.append(gen_trace("markers", 0.5, "grey", street_corners))
        if bus:
            bus_route_shapes = pd.DataFrame(
                conn.execute(select(transit_metadata.tables["bus_route_shapes"]))
            )
            if graph_view:
                bus_geoms = gen_graph_geoms(self.graph, "bus")
            else:
                bus_geoms = MultiLineString(
                    [
                        MultiLineString(segment["coordinates"])
                        for segment in bus_route_shapes.geometry
                    ]
                )
            line_traces.append(gen_trace("lines", 1, "black", bus_geoms))
            bus_stops = [node.location for node in self.nodes_by_type["bus"]]
            node_traces.append(gen_trace("markers", 1, "black", bus_stops))
        if rail:
            rail_line_shapes = pd.DataFrame(
                conn.execute(select(transit_metadata.tables["train_line_shapes"]))
            )
            for line in rail_line_shapes.lines.unique():
                if len(line.split(",")) > 1:
                    line_color = "darkkhaki"
                else:
                    line_name = line.lower().split(" ")[0]
                    line_color = [
                        line for line in self.lines if line_name in line.name
                    ][0].color
                if graph_view:
                    rail_geoms = gen_graph_geoms(self.graph, "rail", line_color)
                else:
                    rail_geoms = MultiLineString(
                        [
                            MultiLineString(line["coordinates"])
                            for line in rail_line_shapes[
                                rail_line_shapes.lines == line
                            ].geometry
                        ]
                    )
                line_traces.append(gen_trace("lines", 2, line_color, rail_geoms))
                line_stations = [
                    node.location
                    for node in self.nodes_by_type["rail"]
                    if line_color in node.colors
                ]
                node_traces.append(gen_trace("markers", 2, line_color, line_stations))
        if new_conn:
            efficiency_stats = transit_metadata.tables["efficiency_stats"]
            if asc:
                ordering = efficiency_stats.c[optimization_stat].asc()
            else:
                ordering = efficiency_stats.c[optimization_stat].asc()
            query = (
                select(efficiency_stats.c["node1", "node2", optimization_stat])
                .order_by(ordering)
                .limit(conn_number)
            )
            best_conns = pd.DataFrame(conn.execute(query))
            for col in ["node1", "node2"]:
                best_conns.loc[:, col] = [
                    stop
                    for stop in self.nodes
                    for node in best_conns.loc[:, col]
                    if str(stop) == node
                ]
            new_conn_geom = [
                [
                    [row.node1.long(), row.node1.lat()],
                    [row.node2.long(), row.node2.lat()],
                ]
                for i, row in best_conns[["node1", "node2"]].iterrows()
            ]
            line_traces.append(gen_trace("lines", 2, "lawngreen", new_conn_geom))

    centering_layer = min(self.nodes_by_type.values(), key=len)
    center_coords = barycenter(subgraph(self.graph, centering_layer))[0].location
    longitude = center_coords.x
    latitude = center_coords.y
    center = dict(lat=latitude, lon=longitude)

    fig = go.Figure(
        layout=go.Layout(
            title=dict(text=f"<br>{self.city}", font=dict(size=16)),
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=[
                dict(
                    text=f"Map of {self.city}'s rapid transit network",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.005,
                    y=-0.002,
                )
            ],
            map=dict(center=center, zoom=10, bearing=0, pitch=0, style=style),
        ),
    )

    for trace in line_traces + node_traces:
        fig.add_trace(trace)
    fig.show()


def plot_subgraphs(self, center=(0, 0)):
    """
    Plots all disconnected sub-graphs of network. Largely used for testing and analysis if the graph primitive
    ends up being diconnected.

    :param center: latitude and longitude location on which to center the plot
    """
    from networkx import connected_components
    from plotly import graph_objects as go
    from shapely import MultiLineString
    from plotting.utils import gen_trace

    main_g = max(connected_components(self.graph), key=len)
    print(f"subgraph sizes: {[len(c) for c in connected_components(self.graph)]}")
    subgraphs = [
        self.graph.subgraph(c)
        for c in connected_components(self.graph)
        if len(c) < len(main_g)
    ]
    center = dict(lat=center[1], lon=center[0])
    fig = go.Figure(
        layout=go.Layout(
            title=dict(text=f"<br>Chicago", font=dict(size=16)),
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=[
                dict(
                    text=f"Map of Chicago's rapid transit network",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.005,
                    y=-0.002,
                )
            ],
            map=dict(center=center, zoom=10, bearing=0, pitch=0, style="light"),
        ),
    )

    line_traces = []
    node_traces = []
    for g in subgraphs:
        nodes = g.nodes()
        edges = g.edges()
        line_geoms = MultiLineString(
            [
                [
                    (edge[0].location.x, edge[0].location.y),
                    (edge[1].location.x, edge[1].location.y),
                ]
                for edge in edges
            ]
        )
        node_geoms = [node.location for node in nodes]
        line_traces.append(gen_trace("lines", 1, "black", line_geoms))
        node_traces.append(gen_trace("markers", 1, "black", node_geoms))

    for trace in line_traces + node_traces:
        fig.add_trace(trace)
    fig.show()
