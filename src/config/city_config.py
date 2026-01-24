from schema import OpenStreetMapCityName, City

city_map = {
    "chicago": City(
        name="chicago", open_street_map_city_name=OpenStreetMapCityName.CHICAGO
    ),
    "roseburg": City(
        name="roseburg", open_street_map_city_name=OpenStreetMapCityName.ROSEBURG
    )
}
