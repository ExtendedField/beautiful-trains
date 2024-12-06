class Station:
    """A data structure for station information within the urban rapid transit network"""

    name = None # string name of station
    network_id = None
    location = None # lat and long coordinates save in standard (x,y) format for plotting
    lines = None # list of strings corresponding to line names present at station

    def __init__(self, net_id, name="", location=(0,0), lines=None):
        if lines is None:
            lines = []

        if not isinstance(net_id, int):
            raise Exception("Please provide an integer as your station ID")

        self.network_id = net_id
        self.name = name
        self.location = location
        self.lines = lines

    def lat(self):
        return self.location[1]

    def long(self):
        return self.location[0]

    def connects(self, potential_connection) -> bool:
        from numpy import sqrt
        # if the passed station connects to this one, return true, otherwise, return false
        # Connection clues: is the station on the same line?
        overlapping_lines = [line for line in self.lines if line in potential_connection]

        if len(overlapping_lines) < 1:
            return False
        elif (sqrt(self.long()-potential_connection.long()) ** 2) + (sqrt(self.lat()-potential_connection.lat()) ** 2) < 0.02:
            return True