class Network:
    city = ""
    lines = set()
    connections = set()
    stations = set()
    matrix = None

    def __init__(self, city=None, lines=None):

        import pandas as pd
        import networkx as nx

        if lines is None:
            lines = set()
        if city is None:
            city = ""

        self.city = city
        self.lines = lines
        unpacked_stations = [line.stations for line in lines]
        self.stations = {station for station_set in unpacked_stations for station in station_set}
        unpacked_connections = [line.connections for line in lines]
        self.connections = {connections for connections_set in unpacked_connections for connections in connections_set}

        # below suppresses performance warnings caused by repeated insertions into frame
        from warnings import simplefilter
        simplefilter(action="ignore", category=pd.errors.PerformanceWarning)

        # build matrix from lines list
        network_ids = [station.network_id for station in self.stations]
        adj_matrix = pd.DataFrame(0, columns=network_ids, index=network_ids)
        for connection in self.connections:
            adj_matrix.loc[connection.station1, connection.station2] = 1
        self.matrix = adj_matrix

        # create graph object
        graph = nx.Graph()
        graph.add_nodes_from({line.line_graph for line in lines})



    # def plot ():

    # create functions to return network stats that are of interest
