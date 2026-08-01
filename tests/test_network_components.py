from shapely import MultiLineString, Point

from city_network import (
    config as cfg,
)
from city_network import (
    network as net,
)
from city_network import (
    network_components as ntc,
)
from city_network import (
    schemas as schm,
)


def test_creating_node():
    node = ntc.Node(
        net_id="1",
        location=Point(1, 2),
        available_lines=[
            schm.LineColorPair(name="red", color="red"),
            schm.LineColorPair(name="john", color="green"),
        ],
        transit_modes={cfg.TransitMode.WALK, cfg.TransitMode.HEAVY_RAIL},
        name="",
    )
    assert isinstance(node, net.Node)


def test_creating_connection():
    node1 = net.Node(
        net_id="2",
        location=Point(1, 2),
        available_lines=[schm.LineColorPair(name="blue", color="blue")],
        transit_modes={cfg.TransitMode.LIGHT_RAIL},
        name="test_node1",
    )
    node2 = net.Node(
        net_id="3",
        location=Point(3, 4),
        available_lines=[schm.LineColorPair(name="yellow", color="yellow")],
        transit_modes={cfg.TransitMode.LIGHT_RAIL},
        name="test_node2",
    )
    connection = net.Connection(
        station1=node1,
        station2=node2,
        transit_modes=[
            cfg.TransitMode.WALK,
            cfg.TransitMode.BUS,
            cfg.TransitMode.LIGHT_RAIL,
        ],
    )
    assert isinstance(connection, net.Connection)


def test_creating_line():
    node_a = net.Node(
        net_id="4",
        location=Point(5, 6),
        available_lines=[schm.LineColorPair(name="purple", color="purple")],
        transit_modes={cfg.TransitMode.LIGHT_RAIL},
        name="",
    )
    node_b = net.Node(
        net_id="5",
        location=Point(7, 8),
        available_lines=[schm.LineColorPair(name="pink", color="pink")],
        transit_modes={cfg.TransitMode.LIGHT_RAIL},
        name="",
    )
    connection = net.Connection(
        station1=node_a,
        station2=node_b,
        transit_modes=[cfg.TransitMode.LIGHT_RAIL],
    )
    line = net.Line(
        stations={node_a, node_b},
        connections={connection},
        line_type=cfg.TransitMode.LIGHT_RAIL,
        name_and_color=schm.LineColorPair(name="red", color="red"),
    )
    assert isinstance(line, net.Line)


def test_creating_network():
    node_x = net.Node(
        net_id="6",
        location=Point(9, 10),
        available_lines=[schm.LineColorPair(name="teal", color="teal")],
        transit_modes={cfg.TransitMode.LIGHT_RAIL},
        name="",
    )
    node_y = net.Node(
        net_id="7",
        location=Point(11, 12),
        available_lines=[schm.LineColorPair(name="orange", color="orange")],
        transit_modes={cfg.TransitMode.LIGHT_RAIL},
        name="",
    )
    connection = net.Connection(
        station1=node_x,
        station2=node_y,
        transit_modes=[cfg.TransitMode.LIGHT_RAIL, cfg.TransitMode.WALK],
    )

    line = net.Line(
        stations={node_x, node_y},
        connections={connection},
        line_type=cfg.TransitMode.LIGHT_RAIL,
        name_and_color=schm.LineColorPair(name="red", color="red"),
    )

    transit_shape = schm.TransitShape(
        line_and_color=schm.LineColorPair(name="red", color="red"),
        shape=MultiLineString([[[9, 10], [11, 12]]]),
    )

    network = net.Network(
        city="Test City",
        lines=[line],
        transit_shapes=[transit_shape],
        walking_shapes=MultiLineString([[[9, 10], [11, 12]]]),
    )
    assert isinstance(network, net.Network)
