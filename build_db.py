from utils import add_to_db, read_city_json, build_table
import argparse
from data.dbmetadata.schemas import schemas
import pickle
from sqlalchemy import (
    create_engine,
    MetaData,
)

# pass in city
parser = argparse.ArgumentParser(
    prog="RT Network Generator",
    description="Generates network structure for a city's rapid transit network",
)
parser.add_argument("city_name")
parser.add_argument("-r", "--refresh", type=bool)
args = parser.parse_args()
city = args.city_name
refresh = args.refresh

city_info = read_city_json(city, "./data/city_info.json")
table_info = city_info["tables"]
# below block will expand as new apis are added
if city_info["client_api"] == "socrata":
    from sodapy import Socrata
    client = Socrata(city_info["website"], city_info["token"])
else:
    raise Exception("Unknown client id. Please try another")

# create and load data into Postgre database
import subprocess

# shell script creates the db with the name "{city}_transitdb" if it does not
# already exist. It also creates a user role called "transitdb_user" if it
# does not already exist
subprocess.run(["sh", "./setupdb.sh", city])

transit_metadata = MetaData()
passwd = "conductor" # encrypt somewhere buddy...
engine = create_engine(
    f"postgresql://transitdb_user:{passwd}@localhost/{city}_transitdb"
)

tables = [build_table(transit_metadata, table_name, schema) for table_name, schema in schemas.items()]
transit_metadata.create_all(engine)
for table in tables:
    table_id = city_info["tables"][table.name]["remote_table_id"]
    local_dir = city_info["tables"][table.name]["local_dir"]
    add_to_db(city, table, engine, client, table_id=table_id, source_csv=local_dir)

print("Pickling DB Metadata...")
directory = f"data/dbmetadata/{city}db_metadata.pkl"
output = open(directory, "wb+")
pickle.dump(transit_metadata, output)
output.close()
print(f"DB Metadata pickled and saved at: {directory}")
