from sodapy import Socrata
from collector_funcs import get_data

# initialize Socrata client for city of chicago data
chicago_client = Socrata("data.cityofchicago.org", None)

# {name: plaintext name, id: socrata dataset_id, path: desired path}
chicago_datasets = [{"name": "'L' Stops", "id":"8pix-ypme", "path":"cta/l-stops.csv"},]
for dataset in chicago_datasets:
    print(get_data(chicago_client, dataset["id"], dataset["path"]).head())
