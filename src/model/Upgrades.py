from enum import Enum

class HumanType(Enum):
    COLON = 1
    MINER = 2
    LUMBERJACK = 3
    FARMER = 4
    #SOLDIER = 5

class Technologies(Enum):
    FORESTRY = 1
    AGRICULTURE = 2
    MINING = 3
    HUNT = 4
    BUILDING_HEALTH = 5
    BUILDING_TIME = 6
    EXTRA_MATERIALS = 7 # TODO: To unlock Crystal and Vulcan