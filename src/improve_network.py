from city_network.network import Network

def find_n_best_new_connections(
    unoptimized_transit_network: Network, n: int = 1
) -> Network:
    optimized_transit_network = unoptimized_transit_network.copy()
    for i in range(n):
        optimized_transit_network = _find_best_new_connection(optimized_transit_network)
    return optimized_transit_network


def _find_best_new_connection(transit_network: Network) -> Network:
    pass

