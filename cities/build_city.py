import rt_network
import argparse
from data.util import get_data

# pass in city
parser = argparse.ArgumentParser(prog='RT Network Generator',
                                 description="Generates network structure for a city's rapid transit network")
parser.add_argument("city_name")
parser.add_argument("-r", "--refresh", type=bool)
args = parser.parse_args()
city = args.city_name
refresh = args.refresh

# fetch relevant data
rt_network_data = get_data(city)

# build network object


# store network object...

