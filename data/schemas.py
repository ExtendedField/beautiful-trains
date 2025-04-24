# contains schema metadata required to construct tables in PostgreSQL database using SQLAlchemy

from sqlalchemy import (
#    ForeignKey,
    Integer,
    String,
    Date,
    Boolean,
    CHAR,
)

# schema structure -> "table_name":{"column_name": {"type": type, "params": {"args": [], "kwargs": {}})}
schemas = {
    "rider_data": {
        "station_id": {
            "type": Integer,
            "params": {"args": [], "kwargs": {"primary_key": True}},
        },
        "station_name": {
            "type": String,
            "params": {
                "args": [],
                "kwargs": {
                    "nullable": False,
                },
            },
        },
        "date": {"type": Date, "params": {"args": [], "kwargs": {"primary_key": True}}},
        "day_type": {"type": CHAR, "params": {"args": [], "kwargs": {}}},
        "rides": {"type": Integer, "params": {"args": [], "kwargs": {}}},
    },
    "station_order": {
        "line": {"type": String, "params": {"args": [], "kwargs": {}}},
        "order": {"type": ARRAY, "params": {"args": [], "kwargs": {}}},
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
                "args": [],
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
        "ada": {"type": Boolean, "params": {"args": [], "kwargs": {}}},
        "red": {"type": Boolean, "params": {"args": [], "kwargs": {}}},
        "blue": {"type": Boolean, "params": {"args": [], "kwargs": {}}},
        "green": {"type": Boolean, "params": {"args": [], "kwargs": {}}},
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
