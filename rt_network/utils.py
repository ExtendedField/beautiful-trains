import pandas as pd
import os
import json

def get_data(city, dataset, refresh=False,) -> pd.DataFrame:
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
        results = client.get(dataset_id)
        print("Data Downloaded.")
    except:
        #maybe make this more informative
        raise Exception("Unable to fetch data. Check table key in city_info.json")

    print(f"Saving data to: {output_dir}")
    list_dir = table_dir.split("/")
    table_target_dir = "/".join(list_dir[:-1]) + "/"
    if not os.path.exists(output_dir):
        os.mkdir(table_target_dir)
    data = pd.DataFrame.from_records(results)
    data.to_csv(table_dir)
    return data

def read_city_json(city, json_dir):
    with open(json_dir) as city_info_json:
        return json.load(city_info_json)[city]


