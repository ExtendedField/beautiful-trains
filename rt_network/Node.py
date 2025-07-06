class Node:
    def __init__(
            self,
            net_id=None,
            name="",
            location=(0, 0),
            lines=None,
            colors=None,
            node_type="street"
    ):
        """
        A data structure for node information within the urban rapid transit network.

        :param net_id: unique identifier of node within the network
        :param name: human-readable name for node
        :param location: tuple of lat and lon coordinates of node
        :param lines: lines available to passengers at node
        :param colors: corresponding colors of lines available to passengers at node
        :param node_type: train station, bus stop, street corner, etc.

        Attributes:
            :node_type: train station, bus stop, street corner, etc.
            :colors: corresponding colors of lines available to passengers at node
            :network_id: unique identifier of node within the network
            :name: human-readable name for node
            :location: shapely Point object for node coordinates on earth
            :lines: lines available to passengers at node
        """
        from shapely import Point

        if lines is None:
            lines = []

        self.node_type = node_type
        if colors is None:
            self.colors = list()
        else:
            if type(colors) is str:
                self.colors = [colors]
            else:
                self.colors = list(colors)

        self.network_id = net_id
        self.name = str(name)
        self.location = Point(location)
        self.lines = list(lines)

    def __str__(self):
        return f"{self.name}: {", ".join(self.lines)}"

    def lat(self):
        """
        :returns: latitude of node
        """
        return self.location.y

    def long(self):
        """
        :returns: latitude of node
        """
        return self.location.x
