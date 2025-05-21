class Network:
    city = ""
    lines = set()
    connections = set()
    stations = set()
    matrix = None
    graph = None

    def __init__(self, city=None, lines=None):
        import pandas as pd
        import networkx as nx
        import numpy as np

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

    def __str__(self):
        return f"{self.city}'s tranist network\nNumber of rail lines: {len(self.lines)}\nTotal stations: {len(self.stations)}"

# implement a voronoi cell plotting function once all nodes are added rather than just rail
    def plot(self, new_conn=None, proj="mercator") -> None:
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
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            ),
        )
        if new_conn:
            if new_conn == "global_efficiency":
                ascending=False
            else:
                ascending=True
            top_ten = (
                self.efficiency_stats.sort_values(
                    by=new_conn, ascending=ascending
                )
                .head(10)
                .index
            )
            for edge in top_ten:
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
            new_edge_trace = go.Scatter(
                x=edge_x,
                y=edge_y,
                line=dict(width=0.5, color="#ff0000"),
                hoverinfo="none",
                mode="lines",
            )
            fig.add_trace(new_edge_trace)
        fig.add_trace(node_trace)
        fig.add_trace(edge_trace)
        fig.show()

    # create functions to return network stats that are of interest
