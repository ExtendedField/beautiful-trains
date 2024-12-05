class Connection:
    import Station
    station1 = None
    station2 = None

    def __init__(self, station1=Station(), station2=Station()):
        station1=station1
        station2=station2

    def distance(self):
        from numpy import sqrt

        x_dist = self.station1.long() - self.station2.long()
        y_dist = self.station1.lat() - self.station2.lat()
        return sqrt(x_dist**2 + y_dist**2) # Euclidean distance. maybe parameterize? probably not
