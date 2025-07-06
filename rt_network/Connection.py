class Connection:
    def __init__(self, station1, station2, conn_type="street"):
        """
        Object containing metadata regarding a connection in the transit network. Often used in project as a way of
        quickly generating distances or temporarily storing connection information.

        :param station1: station on one side of connection
        :param station2: station on the other side of the connection
        :param conn_type: denotes type of connection like 'rail', 'bus', or 'street'

        Attributes:
            station1            station on one side of connection
            station2            station on other side of connection
            travel_resistance   travel time heuristic using the connection type and distance
        """
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
        """
        Returns stations and their resistance as a tuple which conveniently plugs into NetworkX generator functions

        :param weighted: boolean indicating whether the travel resistance should be returned along with the stations.
        :returns: tuple of stations or stations with dictionary of metadata.
                  (station1, station2) or (station1, station2, {metadata})
        """
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
