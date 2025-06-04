import pandas as pd
import json
from tqdm import tqdm
from time import sleep
import numpy as np
import networkx as nx


def build_table(metadata, table_name, schema):
    from sqlalchemy import (
        Table,
        Column,
    )

    columns = [
        Column(
            column_name,
            info["type"],
            *info["params"]["args"],
            **info["params"]["kwargs"],
        )
        for column_name, info in schema.items()
    ]

    table = Table(
        table_name,
        metadata,
        *columns,
    )

    return table


def add_to_db(
    city,
    table,
    engine,
    client=None,  # optional in the case where only a csv or DF is passed
    table_id=None,
    source_csv=None,
    source_df=None,
    query_params=None,
):
    """
    If requested data does not exist in the database, this downloads it and adds it to the db
    """
    from sqlalchemy.dialects.postgresql import insert

    if query_params is None:
        query_params = {}

    table_name = table.name

    if table_id:
        print(f"Fetching table_id: {table_id}")
        try:
            # this syntax may be different with other client APIs. May have to parameterize
            # or use a more generic HTTP request package.
            import itertools

            num_rows = int(
                client.get(table_id, query="select count(*)")[0]["count"]
            )  # this is sure to break with other APIs
            chunk_size = 999  # socrata only allows 1k rows per request.
            num_chunks = round(num_rows / chunk_size) + 1
            offsets = [chunk_size * x for x in range(num_chunks)]
            sleep(0.5) # trying to resolve timeout between large table fetches
            data = client.get(table_id, offset=offsets[0], **query_params)
            if len(offsets) > 1:
                for offset in tqdm(offsets):
                    data.extend(client.get(table_id, offset=offset, **query_params))
                    # if API calls are made too frequently, not all data will be fetched.
                    sleep(0.1)
            print("Data Downloaded.")
        except:
            raise Exception("Unable to fetch data. Check table key in city_info.json")
        # Sodapy appears to skip null values when pulling from table.
        # converting to a DF as an intermediate resolves the issue.
        data = pd.DataFrame(data)
    elif source_csv:
        path = f"data/{source_csv}"
        data = pd.read_csv(path)
        if table.name == "train_station_order":
            data["order"] = data["order"].str.split(",")
    elif source_df is not None:
        data = source_df
    else:
        print(
            f"No table_id, source_csv, or source_df given. Table: {table_name} will be left empty."
        )
        return
    print(f"Writing to table: {city}_transitdb.{table_name}")

    data = [row.to_dict() for i, row in data.iterrows()]  # convert to list of dicts
    print(f"Saving data to table: {table_name}")
    with engine.connect() as conn:
        for row in tqdm(data):
            # repackages data with specified schema names instead of schema defined by the transit org
            renamed_row = dict(zip(table.c.keys(), row.values()))
            query = (
                insert(table)
                .values(renamed_row)
                .on_conflict_do_update(
                    index_elements=table.primary_key, set_=renamed_row
                )
            )
            conn.execute(query)
        conn.commit()

def read_city_json(city, json_dir):
    with open(json_dir) as city_info_json:
        return json.load(city_info_json)[city]

def weighted_shortest_path(g, boardings, weight="travel_resistance"):
    nodes = list(g)
    index = sorted([node.network_id for node in nodes])
    boardings = boardings[boardings.index.isin(index)]
    total_boardings = float(boardings.avg_rides.sum())

    path_lengths = pd.DataFrame(dict(nx.shortest_path_length(g, weight=weight)))
    path_lengths.index = [i.network_id for i in path_lengths.index]
    path_lengths.columns = [i.network_id for i in path_lengths.columns]
    path_lengths = path_lengths.sort_index().sort_index(axis=1)
    return (
        np.matmul(
            np.diag(boardings.to_numpy().flatten()).astype("float"),
            path_lengths,
        ).sum()
        / total_boardings
    ).mean()


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
    if trace_type =='lines':
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
