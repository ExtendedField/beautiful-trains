class Station:
    """A data structure for station information within the urban rapid transit network"""

    name = None  # string name of station
    network_id = None
    location = (
        None  # lat and long coordinates save in standard (x,y) format for plotting
    )
    lines = None  # list of strings corresponding to line names present at station

    def __init__(self, net_id=None, name="", location=(0, 0), lines=None):
        from numpy import int64

        if lines is None:
            lines = []

        if not (isinstance(net_id, int) or isinstance(net_id, int64)):
            raise Exception("Please provide an integer as your station ID")

        self.network_id = net_id
        self.name = name
        self.location = location
        self.lines = lines

    def __str__(self):
        return f"{self.name}\nLocated at:{self.location}"

    def lat(self):
        return self.location[1]

    def long(self):
        return self.location[0]
