class Connection:
    station1 = None
    station2 = None

    def __init__(self, station1=None, station2=None):
        self.station1 = station1
        self.station2 = station2

    def __str__(self):
        return f"{self.station1.name}<->{self.station2.name}"

    def distance(self):
        from numpy import sqrt

        x_dist = self.station1.long() - self.station2.long()
        y_dist = self.station1.lat() - self.station2.lat()
        return sqrt(
            x_dist**2 + y_dist**2
        )  # Euclidean distance. maybe parameterize? probably not

    def get_connection_tuple(self, weighted=False):
        if weighted:
            return self.station1, self.station2, {"weight": self.distance()}
        else:
            return self.station1, self.station2
