# contains schema metadata required to construct tables in PostgreSQL database using SQLAlchemy

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Date,
    Boolean,
    CHAR,
)

# schema structure -> "table_name":{"column_name": {"type": type, "params": {"args": [], "kwargs": {}})}
schemas = {
    "station_id_map": {
        "station_name": {
            "type": String,
            "params": {"args": [], "kwargs": {"unique": True}},
        },
        "station_descriptive_name": {
            "type": String,
            "params": {"args": [], "kwargs": {}},
        },
        "station_id": {
            "type": String,
            "params": {"args": [], "kwargs": {"primary_key": True}},
        },
    },
    "rider_data": {
        "station_id": {
            "type": Integer,
            "params": {"args": [], "kwargs": {"primary_key": True}},
        },
        "station_name": {
            "type": String,
            "params": {
                "args": [
                    ForeignKey("station_id_map.station_name"),
                ],
                "kwargs": {
                    "nullable": False,
                },
            },
        },
        "date": {"type": Date, "params": {"args": [], "kwargs": {}}},
        "rides": {"type": Integer, "params": {"args": [], "kwargs": {}}},
    },
    "station_order": {
        "red": {"type": Integer, "params": {"args": [], "kwargs": {}}},
        "blue": {"type": Integer, "params": {"args": [], "kwargs": {}}},
        "green1": {"type": Integer, "params": {"args": [], "kwargs": {}}},
        "green2": {"type": Integer, "params": {"args": [], "kwargs": {}}},
        "brown": {"type": Integer, "params": {"args": [], "kwargs": {}}},
        "purple": {"type": Integer, "params": {"args": [], "kwargs": {}}},
        "purple_exp": {"type": Integer, "params": {"args": [], "kwargs": {}}},
        "yellow": {"type": Integer, "params": {"args": [], "kwargs": {}}},
        "pink": {"type": Integer, "params": {"args": [], "kwargs": {}}},
        "orange": {"type": Integer, "params": {"args": [], "kwargs": {}}},
    },
    "stations": {
        "stop_id": {
            "type": Integer,
            "params": {"args": [], "kwargs": {"primary_key": True}},
        },
        "direction_id": {"type": CHAR, "params": {"args": [], "kwargs": {}}},
        "station_name": {
            "type": String,
            "params": {
                "args": [
                    ForeignKey("station_id_map.station_name"),
                ],
                "kwargs": {
                    "nullable": False,
                },
            },
        },
        "station_descriptive_name": {
            "type": String,
            "params": {"args": [], "kwargs": {}},
        },
        "map_id": {"type": Integer, "params": {"args": [], "kwargs": {}}},
        "ada": {"type": Integer, "params": {"args": [], "kwargs": {}}},
        "red": {"type": Boolean, "params": {"args": [], "kwargs": {}}},
        "blue": {"type": Boolean, "params": {"args": [], "kwargs": {}}},
        "green1": {"type": Boolean, "params": {"args": [], "kwargs": {}}},
        "green2": {"type": Boolean, "params": {"args": [], "kwargs": {}}},
        "brown": {"type": Boolean, "params": {"args": [], "kwargs": {}}},
        "purple": {"type": Boolean, "params": {"args": [], "kwargs": {}}},
        "purple_exp": {"type": Boolean, "params": {"args": [], "kwargs": {}}},
        "yellow": {"type": Boolean, "params": {"args": [], "kwargs": {}}},
        "pink": {"type": Boolean, "params": {"args": [], "kwargs": {}}},
        "orange": {"type": Boolean, "params": {"args": [], "kwargs": {}}},
        "location": {
            "type": String,  # TODO: figure out how to make this a PostgreSQL "Point" type
            "params": {"args": [], "kwargs": {}},
        },
    },
}
