class Network:
    city = ""
    lines = set()
    connections = set()
    nodes = set()
    graph = None
    rail_shapes = None
    bus_route_shapes = None
    street_shapes = None
    available_modes = set()
    #potentially street, bus, and rail subgraph stored independently

    def __init__(
            self,
            city=None,
            lines=None,
            rail_shapes=None,
            bus_route_shapes=None,
            street_shapes=None
    ):
        import networkx as nx
        import geopandas as gpd
        from shapely import MultiLineString
        import momepy as mp
        from data.resistances import resistances
        from rt_network.Node import Node

        if lines is None:
            lines = set()
        if city is None:
            city = ""

        self.rail_shapes = rail_shapes
        self.bus_route_shapes = bus_route_shapes
        self.street_shapes = street_shapes
        self.city = city
        self.lines = lines
        unpacked_connections = [line.connections for line in lines]
        self.connections = {
            connections
            for connections_set in unpacked_connections
            for connections in connections_set
        }

        # create intersection nodes and how they connect via streets
        street_shapes.loc[:, "geometry"] = [MultiLineString(item["coordinates"]) for item in street_shapes.loc[:, "geometry"]]
        streets = gpd.GeoDataFrame(street_shapes, geometry="geometry").explode()
        street_g = mp.gdf_to_nx(streets)
        mapping = dict()
        for node in street_g:
            mapping[node] = Node(colors="grey", location=node, node_type="street")
        street_g = nx.relabel_nodes(street_g, mapping)
        dists = nx.get_edge_attributes(street_g, name="mm_len")
        for edge_key in dists.keys():
            # mm -> km * resistance factor for walking
            dists[edge_key] = float(dists[edge_key]) * 1000 * resistances["street"]
        nx.set_edge_attributes(street_g, values=dists, name="travel_resistance")

        # create graph object
        graph = street_g
        line_graphs = {line.line_graph for line in lines}
        for lg in line_graphs:
            graph.update(lg)

        #TODO: connect graph layers here...

        self.graph = graph
        self.nodes = graph.nodes()
        self.available_modes = {node.node_type for node in self.nodes}

    def __str__(self):
        return f"{self.city}'s transit network. Number of rail lines: {len(self.lines)}\nTotal nodes: {len(self.nodes)}"

    # TODO: implement a voronoi cell plotting function once all nodes are added rather than just rail
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
        #TODO: add a way to either plot the "true" paths or the graph primitive for testing, illustration
    ) -> None:
        """
        A function to plot a cities rapid transit network as an image, optionally adding in recommended new
        connections.
        """
        # reference link: https://plotly.com/python/network-graphs/
        import plotly.graph_objects as go
        import networkx as nx
        from sqlalchemy import create_engine, select
        import pickle
        import pandas as pd
        from utils import gen_trace
        from shapely import MultiLineString, Point

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
                streets_data = pd.DataFrame(conn.execute(select(transit_metadata.tables["streets"])))
                street_geoms = [MultiLineString(segment["coordinates"]) for segment in streets_data.geometry]
                line_traces.append(gen_trace("lines",0.5, "grey", street_geoms))
            if bus:
                bus_route_shapes = pd.DataFrame(conn.execute(select(transit_metadata.tables["bus_route_shapes"])))
                bus_geoms = [MultiLineString(segment["coordinates"]) for segment in bus_route_shapes.geometry]
                line_traces.append(gen_trace("lines", 1, "black", bus_geoms))
            if rail:
                rail_line_shapes = pd.DataFrame(conn.execute(select(transit_metadata.tables["train_line_shapes"])))
                for line in rail_line_shapes.lines.unique():
                    if len(line.split(",")) > 1:
                        line_color = "darkkhaki"
                    else:
                        line_name = line.lower().split(" ")[0]
                        line_color = [line for line in self.lines if line_name in line.name][0].color
                    rail_geoms = [MultiLineString(line["coordinates"]) for line in rail_line_shapes[rail_line_shapes.lines == line].geometry]
                    line_traces.append(gen_trace("lines", 2, line_color, rail_geoms))
            if new_conn:
                efficiency_stats = transit_metadata.tables["efficiency_stats"]
                if asc:
                    ordering = efficiency_stats.c[optimization_stat].asc()
                else:
                    ordering = efficiency_stats.c[optimization_stat].asc()
                query = (
                    select(
                        efficiency_stats.c[
                            "node1", "node2", optimization_stat
                        ]
                    )
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
                new_conn_geom = [[[row.node1.long(), row.node1.lat()], [row.node2.long(), row.node2.lat()]]
                                 for i, row in best_conns[["node1", "node2"]].iterrows()]
                line_traces.append(gen_trace("lines",2, "lawngreen", new_conn_geom))


        # center location
        longitude, latitude = nx.barycenter(self.graph)[0].location # if multiple, take average of lat and lon
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

        for trace in line_traces:
            fig.add_trace(trace)
        fig.show()