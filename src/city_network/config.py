from enum import Enum, auto


class TransitMode(str, Enum):
    WALK = auto()
    BUS = auto()
    STREETCAR = auto()
    LIGHT_RAIL = auto()
    HEAVY_RAIL = auto()

    def resistance(self):
        resistances = {
            "WALK": 1,
            "BUS": 0.5,
            "STREETCAR": 0.5,
            "LIGHT_RAIL": 0.3,
            "HEAVY_RAIL": 0.2,
        }
        return resistances[self.name]
