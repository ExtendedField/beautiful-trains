class Node:
    """A data structure for station information within the urban rapid transit network"""
    def __init__(self, net_id=None, name="", location=(0, 0), lines=None, colors=None, node_type="street"):
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
        return self.location.y

    def long(self):
        return self.location.x
