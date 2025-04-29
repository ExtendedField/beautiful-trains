import pandas as pd
import json

def add_to_db(city, table, engine, client, table_id=None, source_csv=None, refresh=False, **query_params):
    """
    If requested data does not exist in the database, this downloads it and adds it to the db
    """
    from sqlalchemy.dialects.postgresql import insert
    from sqlalchemy import delete
    table_name = table.name

    if table_id:
        print(f"Fetching table_id: {table_id}")
        try:
            # this syntax may be different with other client APIs. May have to parameterize
            # or use a more generic HTTP request package.
            import itertools
            num_rows = int(client.get(table_id, query="select count(*)")[0]["count"]) # this is sure to break with other APIs
            chunk_size = 999 # socrata only allows 1k rows per request.
            num_chunks = round(num_rows/chunk_size) + 1
            offsets = [chunk_size * x for x in range(num_chunks)]
            data = client.get(table_id, offset=offsets[0], **query_params)
            if len(offsets) > 1:
                for offset in offsets: # add [-100:] to avoid throttling for now
                    data.extend(client.get(table_id, offset=offset, **query_params))
            print("Data Downloaded.")
        except:
            # maybe make this more informative
            raise Exception("Unable to fetch data. Check table key in city_info.json")
    elif source_csv:
        path = f"data/{source_csv}"
        data = pd.read_csv(path)
        if table.name == "station_order":
            data["order"] = data["order"].str.split(",")
        data = [row.to_dict() for i, row in data.iterrows()] # convert to list of dicts
    else:
        print("No table_id or source_csv given. Data not added.")
        return
    print(f"Writing to table: {city}_transitdb.{table_name}")
    import numpy as np
    data = np.array(data)

    print(f"Saving data to table: {table_name}")
    with engine.connect() as conn:
        if refresh:
            query = delete(table)
            conn.execute(query)
        for row in data:
            # repackages data with specified schema names instead of schema defined by the transit org
            renamed_row = dict(zip(table.c.keys(),row.values()))
            query = insert(table).values(tuple(row.values())).on_conflict_do_update(index_elements=table.primary_key,
                                                                                    set_=renamed_row)
            conn.execute(query)
        conn.commit()

def read_city_json(city, json_dir):
    with open(json_dir) as city_info_json:
        return json.load(city_info_json)[city]


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

def build_table(metadata, table_name, schema):
    # return: probably nothing but maybe the metadata object.
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
