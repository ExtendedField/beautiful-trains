class Connection:
    station1 = None
    station2 = None
    distance = 1
    max_speed = None #TODO: add max_speeed to all connections based on speed zones

    def __init__(self, station1=None, station2=None, exists=False):
        self.station1 = station1
        self.station2 = station2
        from numpy import sqrt, cos

        long1 = self.station1.long()
        long2 = self.station2.long()
        lat1 = self.station1.lat()
        lat2 = self.station2.lat()
        deglen = 110.25 #fixed lengths of a degree of latitude on earth

        x_dist = long1 - long2
        y_dist = (lat1 - lat2) * cos(long2)
        self.distance = deglen * sqrt(
            x_dist ** 2 + y_dist ** 2
        )  # Euclidean distance. maybe parameterize? probably not

    def __str__(self):
        return f"{self.station1.name}<->{self.station2.name}"

    def get_connection_tuple(self, weighted=False):
        if weighted:
            return self.station1, self.station2, {"distance": self.distance}
        else:
            return self.station1, self.station2
