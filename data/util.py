import pandas as pd
import os
from sodapy import Socrata
import json

def get_data(city, refresh=False,):
    """
    Checks if data is present locally. If it is, the data is returned. If it is not, the data
    is downloaded, written to the expected directory, and then returned. If refresh=True, the data
    is downloaded by force.
    """

    # one day we will un-hard-code this
    output_dir = "~/project_repos/beautiful-trains/data/" + table_dir
    # Attempt to locate data locally and return it.
    print(f"Fetching table_id: {dataset_id}\nWriting to Directory: {output_dir}")
    if not refresh:
        try:
            print(f"Data found at: {output_dir}\nReturning table...")
            return pd.read_csv(output_dir)
        except FileNotFoundError:
            print(f"Data not found at directory: {output_dir}. Downloading...")

    try:
        # this may break if we use other client APIs. May have to parameterize
        results = client.get(dataset_id)
        print("Data Downloaded.")
    except:
        #maybe make this more informative
        raise Exception("Unable to fetch data. Exiting...")

    print(f"Saving data to: {output_dir}")
    list_dir = table_dir.split("/")
    table_target_dir = "/".join(list_dir[:-1]) + "/"
    if not os.path.exists(output_dir):
        os.mkdir(table_target_dir)
    data = pd.DataFrame.from_records(results)
    data.to_csv(table_dir)
    return data

def refresh_data(json_path, target_cities=None, refresh=False):
    with open(json_path) as city_info_json:
        city_info = json.load(city_info_json)
    if not target_cities:
        target_cities = city_info.keys()

    target_cities = [city for city in target_cities if city in list(city_info.keys())]

    for city_name in target_cities:
        city = city_info[city_name]
        # initialize Socrata client for city of chicago data
        if city['client_api'] == "socrata":
            client = Socrata(city['website'], city['token'])
        else:
            raise Exception("Unknown client id. Please try another")
        # locate or download datasets
        datasets = city['datasets']
        for dataset_key in datasets:
            dataset = datasets[dataset_key]
            print(get_data(client, dataset['table_id'], dataset['local_dir'], refresh).head())