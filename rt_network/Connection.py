class Connection:
    def __init__(self, station1=None, station2=None, conn_type="street"):
        self.station1 = station1
        self.station2 = station2
        from numpy import sqrt, cos
        from data.resistances import resistances

        self.conn_type = conn_type

        long1 = self.station1.long()
        long2 = self.station2.long()
        lat1 = self.station1.lat()
        lat2 = self.station2.lat()
        deglen = 110.25  # fixed lengths of a degree of latitude on earth

        x_dist = long1 - long2
        y_dist = (lat1 - lat2) * cos(long2)
        # Euclidean distance.
        self.travel_resistance = deglen * sqrt( # kms
            x_dist**2 + y_dist**2
        )  * resistances[conn_type]

    def __str__(self):
        return f"{self.station1.name}<->{self.station2.name}"

    def get_connection_tuple(self, weighted=False):
        if weighted:
            return (
                self.station1,
                self.station2,
                {
                    "travel_resistance": self.travel_resistance,
                    "connection_type": self.conn_type,
                    "lines": set(self.station1.lines + self.station2.lines),
                    "colors": set(self.station1.colors + self.station2.colors)
                }
            )
        else:
            return self.station1, self.station2
