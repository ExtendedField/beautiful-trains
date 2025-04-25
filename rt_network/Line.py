class Line:

    name = ""  # usually a color or letter. "green line" or "M line" for example
    stations = set()
    connections = set()
    line_graph = None

    def __init__(self, stations=None, connections=None, name=None, weighted=False):
        import networkx as nx

        if stations is None:
            stations = set()
        self.stations = stations

        if connections is None:
            connections = set()
        self.connections = connections

        if name is None:
            name = ""
        self.name = name

        graph = nx.Graph()
        graph.add_nodes_from(stations)
        graph.add_edges_from(
            [connection.get_connection_tuple(weighted) for connection in connections]
        )

        # remove legacy stations with no connections
        active_stations = [connection.station1 for connection in self.connections] + [
            connection.station2 for connection in self.connections
        ]
        graph.remove_nodes_from(
            [station for station in self.stations if station not in active_stations]
        )

        self.line_graph = graph

    def __str__(self):
        return f"{self.name} line\nnumber of stations:{len(self.stations)}"