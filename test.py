from utils import get_data, build_table
from sqlalchemy import MetaData, create_engine
from data.schemas import schemas

city = "chicago"

transit_metadata = MetaData()
passwd = "conductor"
engine = create_engine(
    f"postgresql://transitdb_user:{passwd}@localhost/{city}_transitdb"
)
table_name = "rider_data"

rider_data = build_table(transit_metadata, table_name, schemas[table_name])

get_data(city, rider_data, engine, transit_metadata, order="date DESC", limit=1000)