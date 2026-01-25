from collect_data.schema import CityConfig
import json


# TODO: make this a pydantic schema not a dict
def initialize_client(city_config: dict):
    pass


def get_city_config(city: str) -> CityConfig:
    with open("./config/city_config.json") as city_config_json:
        city_dict = json.load(city_config_json)[city]
        return CityConfig(
            name=city_dict.get("name", ""),
        )


def connect_closest(eps, route_connections):
    """
    Connects closest two endpoints in a set which do not belong to the same continuous line segment.

    :param eps: set of endpoints
    :param route_connections: set of connections for the current route (bus line, rail line, etc.)
    """
    if len({val["id"] for val in eps.values()}) < 2:
        return
    else:
        ep_list = list(eps.keys())
        ids = {node["id"] for node in eps.values()}
        dists = dict()
        for identifier in ids:
            curr_seg = {ep for ep in ep_list if eps[ep]["id"] == identifier}
            other_segs = {ep for ep in ep_list if eps[ep]["id"] != identifier}
            for curr_ep in curr_seg:
                for other_ep in other_segs:
                    dists[curr_ep.location.distance(other_ep.location)] = {
                        curr_ep,
                        other_ep,
                    }
        closest = tuple(dists[min(dists.keys())])
        route_connections.add(Connection(*closest, conn_type="bus"))
        # give new id to endpoints of newly created line segment
        invalid_ids = {eps[node]["id"] for node in closest}
        for node in eps.keys():
            if eps[node]["id"] in invalid_ids:
                eps[node]["id"] = max(ids) + 1
        connect_closest(eps, route_connections)
