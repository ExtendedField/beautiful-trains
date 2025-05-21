# contains schema metadata required to construct tables in PostgreSQL database using SQLAlchemy

from sqlalchemy import (
    # ForeignKey,
    Integer,
    Numeric,
    String,
    Date,
    Boolean,
    CHAR,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSON

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
        "line": {
            "type": String,
            "params": {"args": [], "kwargs": {"primary_key": True}},
        },
        "order": {"type": ARRAY(Integer), "params": {"args": [], "kwargs": {}}},
    },
    "stations": {
        "stop_id": {
            "type": Integer,
            "params": {"args": [], "kwargs": {"primary_key": True}},
        },
        "direction_id": {"type": CHAR, "params": {"args": [], "kwargs": {}}},
        "stop_name": {"type": String, "params": {"args": [], "kwargs": {}}},
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
            "type": JSON,
            "params": {"args": [], "kwargs": {}},
        },
    },
    # "train_timings":{
    #     "station_id": {"type": Integer, "params": {"args": [], "kwargs": {}}},
    #     "day": {"type": Date, "params": {"args": [], "kwargs": {}}},
    #     "arrival_times": {"type": ARRAY(String), "params": {"args": [], "kwargs": {}}},
    # }, # uncomment when data is located
    "efficiency_stats":{
        "station1": {"type": String, "params": {"args": [], "kwargs": {"primary_key": True}}},
        "station2": {"type": String, "params": {"args": [], "kwargs": {"primary_key": True}}},
        "mean_shortest_path_length": {"type": Numeric, "params": {"args": [], "kwargs": {}}},
        "weighted_shortest_path": {"type": Numeric, "params": {"args": [], "kwargs": {}}},
        "global_efficiency": {"type": Numeric, "params": {"args": [], "kwargs": {}}},
        #"mean_distance_to_nearest_2": {"type": Numeric, "params": {"args": [], "kwargs": {}}},
        #"mean_distance_to_nearest_5": {"type": Numeric, "params": {"args": [], "kwargs": {}}},
        "barycenter": {"type": ARRAY(String), "params": {"args": [], "kwargs": {}}},
        "eccentricity": {"type": ARRAY(Numeric), "params": {"args": [], "kwargs": {}}},
        "avg_clustering": {"type": Numeric, "params": {"args": [], "kwargs": {}}},
        #"communicability": {"type": Numeric, "params": {"args": [], "kwargs": {}}},
        "effective_graph_resistance": {"type": Numeric, "params": {"args": [], "kwargs": {}}},
        "pagerank": {"type": JSON, "params": {"args": [], "kwargs": {}}},
        #"smallworld_sigma": {"type": Numeric, "params": {"args": [], "kwargs": {}}},
        #"smallworld_omega": {"type": Numeric, "params": {"args": [], "kwargs": {}}},
    }
}
