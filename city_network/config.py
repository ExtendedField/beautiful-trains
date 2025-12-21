from enum import Enum

from city_network.schemas import ModeResistancePair


class TransitModeAndResistance(Enum):
    WALK = ModeResistancePair(mode="walk", resistance=1)
    BUS = ModeResistancePair(mode="bus", resistance=0.5)
    STREETCAR = ModeResistancePair(mode="streetcar", resistance=0.5)
    LIGHT_RAIL = ModeResistancePair(mode="light_rail", resistance=0.3)
    HEAVY_RAIL = ModeResistancePair(mode="heavy_rail", resistance=0.2)
