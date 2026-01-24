# TODO: split into two functions, one for lines and one for points and refactor in network.py accordingly.
from shapely import MultiLineString, LineString


def gen_trace(trace_type, line_width, color, geom_data):
    """
    trace_type: 'line' or 'marker'
    line_width: float value of the desired line width
    color: line color
    geom_data: list[MultiLineString] list of shapely MultiLineString objects
               or list[Point] shapely Point objects.
    """
    from plotly import graph_objects as go

    edge_x = []
    edge_y = []
    if trace_type == "lines":
        for segment in geom_data.geoms:
            if ~segment.is_empty:
                for coord in segment.coords:
                    lon = coord[0]
                    lat = coord[1]
                    edge_x.append(lon)
                    edge_y.append(lat)
                edge_x.append(None)
                edge_y.append(None)
    else:
        for coord in geom_data:
            lon = coord.x
            lat = coord.y
            edge_x.append(lon)
            edge_y.append(lat)

    return go.Scattermap(
        lat=edge_y,
        lon=edge_x,
        line=dict(width=line_width, color=color),
        hoverinfo="none",
        mode=trace_type,
    )


# TODO: remove parameterization and rename project_mercator
def project(lam, phi, proj="mercator", deg=True):
    """
    Projects latitude (phi) and longitude (lam) to the cartesian system using the specified projection formula.
    We first convert from degrees to radians if deg is True to ensure the mathe works as expected

    :param phi: latitude
    :param lam: longitude
    :param proj: projection formula name
    :param deg: flag whether the passed coordinates are in degrees.
    :return: (x, y) according to the passed projection formula
    """
    import math

    if deg:
        deg_to_rad = math.pi / 180
        lam = lam * deg_to_rad
        phi = phi * deg_to_rad

    if proj == "mercator":
        x = lam
        y = math.log(math.tan((math.pi / 4) + (phi / 2)))
    else:
        raise Exception(f"Projection formula invalid.\nPassed formula name: {proj}")

    return x, y


def gen_graph_geoms(g, layer, color=None):
    """
    Generates shapely geometry objects to be used for plotting from a NetworkX graph object

    :param g: NetworkX graph object
    :param layer: layer of graph (rail, bus, street, etc.)
    :param color: target color for filtering layer down to specific line
    :returns: MultiLineString in correct format for plotting
    """
    if color:
        condition = lambda u, v: layer in {u.node_type, v.node_type} and color in set(
            u.colors + v.colors
        )
    else:
        condition = lambda u, v: layer in {u.node_type, v.node_type}
    return MultiLineString(
        [LineString((u.location, v.location)) for u, v in g.edges() if condition(u, v)]
    )
