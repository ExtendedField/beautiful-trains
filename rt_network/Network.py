class Network:
    # import Line

    city = ""
    lines = set()
    connections = set()
    stations = set()
    matrix = None

    def __init__(self, city=None, lines=None):
        if lines is None:
            lines = set()
        if city is None:
            city = ""

        self.lines = lines

        # find connections between lines

        # build matrix from lines list


    # def plot ():

    # create functions to return network stats that are of interest
