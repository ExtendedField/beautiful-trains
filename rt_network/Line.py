class Line:
    # from rt_network.Station import Station
    # from rt_network.Connection import Connection

    name = "" # usually a color or letter. "green line" or "M line" for example
    stations = set()
    connections = set()

    def __init__(self, stations=None, connections=None, name = None):
        if stations is None:
            stations = set()
        self.stations = stations

        if connections is None:
            connections = set()
        self.connections = connections

        if name is None:
            name = ""
        self.name = name
