from sqlalchemy import Table
import json
from time import sleep

import pandas as pd
from sqlalchemy import MetaData
from tqdm import tqdm

from city_network.network_components import Connection




# TODO: make schema with pydantic
def build_table(metadata: MetaData, table_name: str, schema) -> Table:
    """
    Creates and returns an SQLAlchemy table object from a simple schema.

    :param metadata: SQLAlchemy metadata object for the database.
    :param table_name: table name
    :param schema: desired schema imported from schemas.py
    """
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


# TODO: split into 3 functions, one for each case handled by this one, and refactor acordingly in build_db
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
    If requested data does not exist in the database, this downloads it, loads it from csv, or loads it from DataFrame
    and adds it to the db.

    :param city: city name
    :param table: table name
    :param engine: SQLAlchemy engine object
    :param client: client used to download remote data. Optional if csv or df is passed
    :param table_id: remote server table id
    :param source_csv: a csv from which the db table will be created
    :param source_df: a DataFrame from which the db table will be created
    :param query_params: any query parameters used for an SQL style query of a data server
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
            sleep(0.5)  # trying to resolve timeout between large table fetches
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





def connect_closest(eps, route_connections):
    """
    Connects closest two endpoints in a set which do not belong to the same continuous line segment.

    :param eps: set of endpoints
    :param route_connections: set of connections for the current route (bus line, rail line, etc.)
    """
    if len({val["id"] for val in eps.values()}) < 2:
        return
    else:
        ep_list = list(eps.keys())
        ids = {node["id"] for node in eps.values()}
        dists = dict()
        for identifier in ids:
            curr_seg = {ep for ep in ep_list if eps[ep]["id"] == identifier}
            other_segs = {ep for ep in ep_list if eps[ep]["id"] != identifier}
            for curr_ep in curr_seg:
                for other_ep in other_segs:
                    dists[curr_ep.location.distance(other_ep.location)] = {
                        curr_ep,
                        other_ep,
                    }
        closest = tuple(dists[min(dists.keys())])
        route_connections.add(Connection(*closest, conn_type="bus"))
        # give new id to endpoints of newly created line segment
        invalid_ids = {eps[node]["id"] for node in closest}
        for node in eps.keys():
            if eps[node]["id"] in invalid_ids:
                eps[node]["id"] = max(ids) + 1
        connect_closest(eps, route_connections)
