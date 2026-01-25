from collect_data.collect_data import get_city_networks
from schema import City
from config.city_config import city_osm_query_values


def improve_city(city: City):
    public_transit_network, walking_network = get_city_networks(city)
    print(public_transit_network, walking_network)
    # improve_public_transit(city)
    # plot_improved_transit(city)


def improve_public_transit(city: City):
    pass


def plot_improved_transit(city: City):
    pass


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog="RT Network Analyzer",
        description="Improves a city's rapid transit network",
    )
    parser.add_argument("city_name")
    args = parser.parse_args()
    city = args.city_name
    try:
        osm_city_query = city_osm_query_values[city].value
    except:
        print("City shortname not found in city_config.py. Trying passed name directly")
        # TODO: would be great to validate this against Nominatim
        osm_city_query = city
    improve_city(
        City(
            name=city,
            open_street_map_city_name=osm_city_query,
        )
    )
