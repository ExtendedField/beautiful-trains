class Network:
    city = ""
    lines = set()
    connections = set()
    stations = set()
    graph = None

    def __init__(self, city=None, lines=None):
        import networkx as nx

        if lines is None:
            lines = set()
        if city is None:
            city = ""

        self.city = city
        self.lines = lines
        unpacked_stations = [line.stations for line in lines]
        self.stations = {
            station for station_set in unpacked_stations for station in station_set
        }
        unpacked_connections = [line.connections for line in lines]
        self.connections = {
            connections
            for connections_set in unpacked_connections
            for connections in connections_set
        }

        # create graph object
        graph = nx.Graph()
        line_graphs = {line.line_graph for line in lines}
        for lg in line_graphs:
            graph = nx.compose(graph, lg)
        self.graph = graph

    def __str__(self):
        return f"{self.city}'s transit network. Number of rail lines: {len(self.lines)}\nTotal stations: {len(self.stations)}"

# implement a voronoi cell plotting function once all nodes are added rather than just rail
    def plot_map(self,
                 new_conn=False,
                 optimization_stat="mean_shortest_path_length",
                 asc=True,
                 conn_number=10) -> None:
        """A Method to plot the RT network as a visio-spacial graph"""
        # reference link: https://plotly.com/python/network-graphs/
        import plotly.graph_objects as go
        import networkx as nx

        #TODO: color lines based on their color rather than being all the same.
        g = self.graph
        edge_x = []
        edge_y = []
        for edge in g.edges():
            lam0 = edge[0].long()
            phi0 = edge[0].lat()
            #x0, y0 = project(lam0, phi0, proj)
            lam1 = edge[1].long()
            phi1 = edge[1].lat()
            #x1, y1 = project(lam1, phi1, proj)
            edge_x.append(lam0)
            edge_x.append(lam1)
            edge_x.append(None)
            edge_y.append(phi0)
            edge_y.append(phi1)
            edge_y.append(None)

        edge_trace = go.Scattermap(
            lat=edge_y,
            lon=edge_x,
            line=dict(width=0.5, color="black"),
            hoverinfo="none",
            mode="lines",
        )

        node_x = []
        node_y = []
        node_text = []
        for node in g.nodes():
            lam = node.long()
            phi = node.lat()
            # x, y = project(lam, phi, proj)
            node_x.append(lam)
            node_y.append(phi)
            node_text.append(f"Name: {node.name}\nID: {node.network_id}")

        node_trace = go.Scattermap(
            lat=node_y,
            lon=node_x,
            mode="markers",
            hoverinfo="text",
            marker=go.scattermap.Marker(size=9),
        )

        node_trace.text = node_text

        # map scale logic
        lon, lat = nx.barycenter(self.graph)[0].location
        center = dict(lat=lat,lon=lon)

        fig = go.Figure(
            layout=go.Layout(
                title=dict(
                    text=f"<br>{self.city}", font=dict(size=16)
                ),
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
                map=dict(center=center,
                         zoom=10,
                         bearing=0,
                         pitch=0,
                         style='light')
            ),
        )
        if new_conn:
            from sqlalchemy import create_engine, select
            import pickle
            import pandas as pd
            passwd = "conductor"  # encrypt somewhere buddy...
            engine = create_engine(
                f"postgresql://transitdb_user:{passwd}@localhost/{self.city}_transitdb"
            )

            # unpickle metadata object...
            filedir = f"data/dbmetadata/{self.city}db_metadata.pkl"
            with open(filedir, "rb") as f:
                transit_metadata = pickle.load(f)

            with engine.connect() as conn:
                efficiency_stats=transit_metadata.tables["efficiency_stats"]
                if asc:
                    query = select(efficiency_stats.c["station1", "station2", optimization_stat]).order_by(
                        efficiency_stats.c[optimization_stat].asc()).limit(conn_number)
                else:
                    query = select(efficiency_stats.c["station1", "station2", optimization_stat]).order_by(
                        efficiency_stats.c[optimization_stat].desc()).limit(conn_number)

                best_conns = pd.DataFrame(conn.execute(query))
                for col in ["station1", "station2"]:
                    best_conns.loc[:,col] = [stop for stop in self.stations for station in best_conns.loc[:,col] if str(stop) == station]

            for i, row in best_conns.iterrows():
                lam0 = row.station1.long()
                phi0 = row.station1.lat()
                #x0, y0 = project(lam0, phi0, proj)
                lam1 = row.station2.long()
                phi1 = row.station2.lat()
                #x1, y1 = project(lam1, phi1, proj)
                edge_x.append(lam0)
                edge_x.append(lam1)
                edge_x.append(None)
                edge_y.append(phi0)
                edge_y.append(phi1)
                edge_y.append(None)

            new_edge_trace = go.Scattermap(
                lat=edge_y,
                lon=edge_x,
                line=dict(width=0.5, color="red"),
                hoverinfo="none",
                mode="lines",
            )
            fig.add_trace(new_edge_trace)
        fig.add_trace(node_trace)
        fig.add_trace(edge_trace)
        fig.show()

    # create functions to return network stats that are of interest
