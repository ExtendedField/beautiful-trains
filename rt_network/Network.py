class Network:
    stations = None
    connections = None
    matrix = None

    def __init__(self, stations_list = None, connections_list=None):
        if stations_list is None:
            stations_list = []
        self.stations = stations_list

        if connections_list is None:
            connections_list = []
        self.connections = connections_list

        # build matrix from connections list


    # def plot ():

    # create functions to return network stats that are of interest
