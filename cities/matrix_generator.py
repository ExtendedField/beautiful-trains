from data.utils import refresh_data
import pandas as pd
import numpy as np
from ast import literal_eval
from matplotlib import pyplot as plt

def process_station(station, line_options):
    stop_name = station.stop_name
    # below selects the indexes corresponding to the line colors/labels and then filters for which line/s
    # are flagged as true. there is likely a better way to do this...
    line_labels = station[line_options]
    available_lines = line_labels.index[np.nonzero(line_labels)] # all lines a passenger will find at this station
    raw_loc = literal_eval(station.location)
    # this order was chose to mirror the "x/y" coordinate convention typically used in mathematics
    # longitude is thought of as an "x" measurement here and latitude as the "y" measurement
    coordinates = (float(raw_loc['longitude']), float(raw_loc['latitude']))

    return {"stop_name" : stop_name, "available_lines": available_lines, "coordinates": coordinates}

def plot_network(line_color_map, network_data):
    fig, ax = plt.subplots()
    for line in line_color_map.keys():
        mask = network_data['available_lines'].apply(lambda x: line in x)
        curr_line = network_data[mask]
        x = [coord[0] for coord in curr_line.coordinates] # longitude
        y = [coord[1] for coord in curr_line.coordinates] # latitude
        ax.scatter(x,y, c=line_color_map[line])

    plt.show()

target_cities = ["chicago"]

# refresh city data
# refresh_data('../data/city_data_locations.json', target_cities)

# raw data
l_stops = pd.read_csv("../data/cta/l-stops.csv")
lines = ["red", "blue", "g", "brn", "p", "pexp", "y", "pnk", "o"]
colors = ['r', 'b', 'g', 'tab:brown', 'tab:purple', 'tab:purple', 'y', 'tab:pink', 'tab:orange']
color_map = dict(zip(lines, colors))

station_locations = {"stop_name" : [], "available_lines": [], "coordinates": []}
for index, station in l_stops.iterrows():
    station_info = process_station(station, lines)
    for key in station_info.keys():
        station_locations[key].append(station_info[key])

network_plot_data = pd.DataFrame.from_dict(station_locations)
plot_network(color_map, network_plot_data)

# print(network_plot_data[network_plot_data.available_lines.apply(len) > 1].available_lines)