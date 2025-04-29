class Network:
    city = ""
    lines = set()
    connections = set()
    stations = set()
    matrix = None
    graph = None
    cluster_coef_list = None
    glob_cluster_coef = None
    degree_dist = None
    wghtd_avg_path_len = None
    potential_connections = None

    def __init__(self, city=None, lines=None):

        import pandas as pd
        import networkx as nx
        from sqlalchemy import create_engine, select, func
        import pickle
        from statistics import mean
        from tqdm import tqdm

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

        # build matrix from lines list
        network_ids = [station.network_id for station in self.stations]
        adj_matrix = pd.DataFrame(0, columns=network_ids, index=network_ids)
        for connection in self.connections:
            adj_matrix.loc[
                connection.station1.network_id, connection.station2.network_id
            ] = 1
        self.matrix = adj_matrix

        # create graph object
        graph = nx.Graph()
        line_graphs = {line.line_graph for line in lines}
        for lg in line_graphs:
            graph = nx.compose(graph, lg)
        self.graph = graph

        # generate network stats
        self.cluster_coef_list = list(nx.clustering(self.graph).values())
        self.glob_cluster_coef = sum(self.cluster_coef_list) / len(
            self.cluster_coef_list
        )
        self.avg_path_len = nx.average_shortest_path_length(self.graph)
        self.degree_dist = nx.degree_histogram(self.graph)

        # average path length from station * daily boardings (average) / total boardings = weighted trip length measure
        def get_weighted_path(g, edge, boardings):
            # this ideally would be drastically more efficient.
            total_boardings = boardings.avg_rides.sum()
            improved_g = g.copy()
            station1, station2 = edge
            improved_g.add_edge(station1, station2)
            path_weights = []
            for source_node in improved_g:
                avg_daily_boardings = boardings.loc[int(source_node.network_id), "avg_rides"]
                avg_path_length = mean([nx.shortest_path_length(improved_g, source_node, target_node)
                                   for target_node in improved_g])
                path_weights.append(float(avg_path_length)*float(avg_daily_boardings)/float(total_boardings))
            improved_g.remove_edge(station1, station2)
            return sum(path_weights)/len(path_weights)

        passwd = "conductor"  # encrypt somewhere buddy...
        engine = create_engine(
            f"postgresql://transitdb_user:{passwd}@localhost/{city}_transitdb"
        )

        # unpickle metadata object...
        filedir = f"data/dbmetadata/{city}db_metadata.pkl"
        with open(filedir, "rb") as f:
            transit_metadata = pickle.load(f)

        with engine.connect() as conn:
            rider_data = transit_metadata.tables["rider_data"]
            avg_rides = func.avg(rider_data.c.rides).label("avg_rides")
            query = select(rider_data.c.station_id, avg_rides).group_by(rider_data.c.station_id)
            daily_boardings = pd.DataFrame(conn.execute(query)).set_index("station_id")

        # create a list of all connections that do not exist in graph (between lines only)
        print("Fetching weighted average path lengths for all possible new connections...")
        # TODO: implement inline loading tracker here. How hard could it be...
        net_complement = nx.complement(self.graph)
        potential_new_connections = [
            edge
            for edge in net_complement.edges
            if list(edge[0].lines) != list(edge[1].lines)
        ]
        path_lengths = pd.DataFrame(
            index=pd.MultiIndex.from_tuples(potential_new_connections),
            columns=["connection_name", "avg_path_length"],
        )
        for connection in tqdm(potential_new_connections):
            new_path_length = get_weighted_path(self.graph, connection, daily_boardings)
            readable_name = f"{connection[0].name} to {connection[1].name}"
            path_lengths.loc[connection, "connection_name"] = readable_name
            path_lengths.loc[connection, "weighted_avg_path_length"] = new_path_length

        self.potential_connections = path_lengths
        self.wghtd_avg_path_len = path_lengths.weighted_avg_path_length.mean()

    def __str__(self):
        return f"{self.city}'s tranist network\nNumber of rail lines: {len(self.lines)}\nTotal stations: {len(self.stations)}"

    def plot(self, proj="mercator") -> None:
        """A Method to plot the RT network as a visio-spacial graph"""
        # reference link: https://plotly.com/python/network-graphs/
        import plotly.graph_objects as go
        from utils import project

        g = self.graph
        edge_x = []
        edge_y = []
        for edge in g.edges():
            lam0 = edge[0].long()
            phi0 = edge[0].lat()
            x0, y0 = project(lam0, phi0, proj)
            lam1 = edge[1].long()
            phi1 = edge[1].lat()
            x1, y1 = project(lam1, phi1, proj)
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=0.5, color="#888"),
            hoverinfo="none",
            mode="lines",
        )

        node_x = []
        node_y = []
        node_text = []
        for node in g.nodes():
            lam = node.long()
            phi = node.lat()
            x, y = project(lam, phi, proj)
            node_x.append(x)
            node_y.append(y)
            node_text.append(f"Name: {node.name}\nID: {node.network_id}")

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers",
            hoverinfo="text",
            marker=dict(
                showscale=True,
                # colorscale options
                # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                colorscale="Greens",
                reversescale=True,
                color=[],
                size=10,
                colorbar=dict(
                    thickness=15,
                    title=dict(text="Node Connections", side="right"),
                    xanchor="left",
                ),
                line_width=2,
            ),
        )

        node_adjacencies = []
        for node, adjacencies in enumerate(g.adjacency()):
            node_adjacencies.append(len(adjacencies[1]))

        node_trace.marker.color = node_adjacencies
        node_trace.text = node_text

        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title=dict(
                    text="<br>Network graph made with Python", font=dict(size=16)
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
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            ),
        )
        fig.show()

    # create functions to return network stats that are of interest
