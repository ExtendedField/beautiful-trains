class Line:
    def __init__(
            self,
            stations=None,
            connections=None,
            name=None,
            color=None,
            weighted=False,
            line_type=None,
    ):
        """
        Object containing metadata regarding a line in the transit network. Used for buses, trains, street cars, or any
        other public transportation mode.

        :param stations: list[Node] of stations which are part of the line (bus stops, train stations, etc...)
        :param connections: list[Connection] of connections between the stations
        :param name: name of line
        :param color: (optional) corresponding color used by city for line
        :param weighted: indicates whether the line's graph primitive should be weighted.
        :param line_type: rail, bus, street, etc..

        Attributes:
            :stations:    stations in line
            :connections: connections in line
            :line_type:   rail, bus, street
            :name:        name of line
            :color:       color of line
            :graph:       graph primitive
        """
        import networkx as nx

        if stations is None:
            stations = set()
        self.stations = stations

        if connections is None:
            connections = set()
        self.connections = connections

        if line_type is None:
            line_type = ""
        self.line_type = line_type

        if name is None:
            name = ""
        self.name = name

        if color is None:
            color = "black"
        self.color = color

        graph = nx.Graph()
        graph.add_nodes_from(stations)
        graph.add_edges_from(
            [connection.get_connection_tuple(weighted) for connection in connections]
        )

        # remove inactive stations with no connections
        active_stations = [connection.station1 for connection in self.connections] + [
            connection.station2 for connection in self.connections
        ]
        graph.remove_nodes_from(
            [station for station in self.stations if station not in active_stations]
        )

        self.line_graph = graph

    def __str__(self):
        return f"{self.name} line. number of stations:{len(self.stations)}"
