from collect_data.collect_data import get_public_transit_network, save_network
from schema import City, NetworkType
from config.city_config import city_map


def improve_city(city: City):
    fetch_data(city)
    # improve_public_transit(city)
    # plot_improved_transit(city)


def fetch_data(city: City):
    print("Collecting Data...")
    city_network = get_public_transit_network(city)
    print("Data Collected.")
    save_network(city, city_network)


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
        improve_city(city_map[city])
    except Exception as e:
        raise Exception(
            f"invalid city name: {city} passed. Valid city names include:"
            f"{city_map.keys()}"
        )
