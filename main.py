def improve_city(city: str):
    fetch_data(city)
    improve_public_transit(city)
    plot_improved_transit(city)


def fetch_data(city: str):
    pass


def improve_public_transit(city: str):
    pass


def plot_improved_transit(city: str):
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
    improve_city(city)
