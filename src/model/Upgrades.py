from enum import Enum

class Technologies(Enum):
    FORESTRY = 1
    AGRICULTURE = 2
    MINING = 3
    HUNT = 4
    COMBAT = 5
    BUILDING_HEALTH = 6
    BUILDING_TIME = 7
    EXTRA_MATERIALS = 8

class Upgrades:
    __slots__ = ["BUILDING_HEALTH_MULTIPLIER", "BUILDING_TIME_MULTIPLIER", "FOOD_MULTIPLIER", "MINING_MULTIPLIER", "WOOD_MULTIPLIER", "HUNT_MULTIPLIER", "COMBAT_MULTIPLIER", "EXTRA_MATERIALS"]

    def __init__(self) -> None:
        self.BUILDING_HEALTH_MULTIPLIER = 1
        self.BUILDING_TIME_MULTIPLIER = 1

        self.FOOD_MULTIPLIER = 1
        self.MINING_MULTIPLIER = 1
        self.WOOD_MULTIPLIER = 1
        self.HUNT_MULTIPLIER = 1
        self.COMBAT_MULTIPLIER = 1
        self.EXTRA_MATERIALS = False