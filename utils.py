import pandas as pd
import os
import json

def get_data(city, dataset, refresh=False, **query_params) -> pd.DataFrame:
    """
    Checks if data is present locally. If it is, the data is returned. If it is not, the data
    is downloaded, written to the expected directory, and then returned. If refresh=True, the data
    is downloaded by force.
    """

    # Loads json info for requested city, initialized the relevant client, and extracts
    # information needed to locate or download the data as necessary.
    json_dir = "./data/city_info.json"
    city_info = read_city_json(city, json_dir)
    table_dir = city_info["local_dir"] + dataset + ".csv"
    dataset_id = city_info["datasets"][dataset]

    # absolute directory is likely necessary unfortunately due to the fact that this method
    # can be called from other directories. If I think of a better way to do this, I will
    # update the code.
    output_dir = "~/project_repos/beautiful-trains/data/" + table_dir
    # Attempt to locate data locally and return it.
    if (not refresh) & (table_dir is not None):
        try:
            print(f"Data found at: {output_dir}\nReturning table...")
            return pd.read_csv(output_dir)
        except FileNotFoundError:
            print(f"Data not found at directory: {output_dir}. Downloading...")

    print(f"Fetching table_id: {dataset_id}\nWriting to Directory: {output_dir}")
    if city_info['client_api'] == "socrata":
        from sodapy import Socrata
        client = Socrata(city_info['website'], city_info['token'])
    else:
        raise Exception("Unknown client id. Please try another")

    try:
        # this syntax may be different with other client APIs. May have to parameterize
        # or use a more generic HTTP request package.
        results = client.get(dataset_id, **query_params)
        print("Data Downloaded.")
    except:
        #maybe make this more informative
        raise Exception("Unable to fetch data. Check table key in city_info.json")

    print(f"Saving data to: {output_dir}")
    list_dir = output_dir.split("/")
    table_target_dir = "/".join(list_dir[:-1]) + "/"
    if not os.path.exists(table_target_dir):
        os.makedirs(table_target_dir)
    data = pd.DataFrame.from_records(results)
    data.to_csv(output_dir)
    return data

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
        deg_to_rad = math.pi/180
        lam = lam * deg_to_rad
        phi = phi * deg_to_rad

    if proj == "mercator":
        x = lam
        y = math.log(math.tan((math.pi/4)+(phi/2)))
    else:
        raise Exception(f"Projection formula invalid.\nPassed formula name: {proj}")

    return x, y

def build_dataset(city):
    from sqlalchemy import (
        create_engine,
        MetaData,
        Table,
        Column,
        ForeignKey,
        Integer,
        String,
        Date,
        Boolean,
        CHAR,
    )
    from geoalchemy2 import Geometry
    import subprocess
    # shell script creates the db with the name "{city}_transitdb" if it does not
    # already exist. It also creates a user role called "transitdb_user" if it
    # does not already exist
    subprocess.run(['sh', './setupdb.sh', city])

    pword = "conductor"
    # create this as high level as you can and pass it down, once you know better where
    # building the db fits into the module. Probably in build city.
    engine = create_engine(f"postgresql://transitdb_user:{pword}@localhost/{city}_transitdb")

    metadata_obj = MetaData()

    # schemas will need to be parameterized to accept other cities transit lines, etc..
    # for now, we will leave this hard coded for chicago
    # TODO: implement a schema file that can easily be parameterized, and find a way to
    #       blow up column definitions based on above schema

    station_id_map = Table(
        "station_id_map",
        metadata_obj,
        Column("station_name", String),
        Column("station_descriptive_name", String),
        Column("station_id", Integer, primary_key=True),
    )

    rider_data = Table(
        "rider_data",
        metadata_obj,
        Column("station_id", Integer, primary_key=True),
        Column("station_name", String, ForeignKey("station_id_map.station_name"), nullable=False),
        Column("date", Date),
        Column("rides", Integer),
    )

    station_order = Table(
        "station_order",
        metadata_obj,
        Column("red", Integer),
        Column("blue", Integer),
        Column("green1", Integer),
        Column("green2", Integer),
        Column("brown", Integer),
        Column("purple", Integer),
        Column("purple_exp", Integer),
        Column("yellow", Integer),
        Column("pink", Integer),
        Column("orange", Integer),
    )

    stations = Table(
        "stations",
        metadata_obj,
        Column("stop_id", Integer, primary_key=True),
        Column("direction_id", CHAR),
        Column("station_name", String, ForeignKey("station_id_map.station_name"), nullable=False),
        Column("station_descriptive_name", String),
        Column("map_id", Integer),
        Column("ada", Integer),
        Column("red", Boolean),
        Column("blue", Boolean),
        Column("green", Boolean),
        Column("brown", Boolean),
        Column("purple", Boolean),
        Column("purple_exp", Boolean),
        Column("yellow", Boolean),
        Column("pink", Boolean),
        Column("orange", Boolean),
        Column("location", Geometry('POINT')),
    )

    # conditional to select relevant data and add tables to dataset in db

