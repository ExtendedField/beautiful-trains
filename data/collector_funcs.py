import pandas as pd
import os

def get_data(client, dataset_id, table_dir, refresh=False,):

    # one day we will un-hard-code this
    output_dir = "~/project_repos/beautiful-trains/data/" + table_dir
    # Attempt to locate data locally and return it.
    if not refresh:
        try:
            print(f"Opening file at: {output_dir}")
            return pd.read_csv(output_dir)
        except FileNotFoundError:
            print(f"Data not found at directory: {output_dir}. Downloading...")

    try:
        results = client.get(dataset_id)
        print("Data Downloaded.")
    except:
        #maybe make this more informative
        raise Exception("Unable to fetch data. Exiting...")


    print(f"Saving data to: {output_dir}")
    list_dir = table_dir.split("/")
    table_target_dir = "/".join(list_dir[:-1])
    if not os.path.exists(output_dir):
        os.mkdir(table_target_dir)
    data = pd.DataFrame.from_records(results)
    data.to_csv(table_dir)
    return data
