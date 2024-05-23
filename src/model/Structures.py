from enum import Enum
import random

from model.Geometry import Point, Rectangle
from model.Ressource import RessourceType
from model.Player import Player

class StructureType(Enum):
    ORE = 1
    BUILDING = 2

class Orientation(Enum):
    RANDOM = 0
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4

class Structure:
    __slots__ = ["structure_type", "coords", "points", "orientation"]

    def __init__(self, structure_type, coords, points, orientation = Orientation.RANDOM) -> None:
        self.structure_type = structure_type
        self.coords = coords
        self.points = points
        self.set_orientation(orientation)
        self.rotate(self.orientation.value - 1)
        
    def set_orientation(self, orientation):
        if orientation == Orientation.RANDOM:
            self.orientation = Orientation(random.randint(1, 4))
        else:
            self.orientation = orientation

    def rotate(self, angle):
        if angle != 0:
            opposite = False
            if angle == 2 or angle == 3:
                opposite = True
            
            invert = False
            if angle == 1 or angle == 3:
                invert = True

            for point in self.points:
                if invert:
                    point.invert()
                if opposite:
                    point.opposite()
    
    def change_orientation(self, orientation):
        old_orientation = self.orientation
        self.set_orientation(orientation)
        self.rotate((old_orientation - self.orientation) % 4)

class OreType(Enum):
    IRON = 1
    COPPER = 2
    GOLD = 3
    VULCAN = 4
    CRYSTAL = 5

oreToRessourceType = {
    OreType.IRON: RessourceType.IRON,
    OreType.COPPER: RessourceType.COPPER,
    OreType.GOLD: RessourceType.GOLD,
    OreType.VULCAN: RessourceType.VULCAN,
    OreType.CRYSTAL: RessourceType.CRYSTAL
}

class Ore(Structure):
    __slots__ = ["type", "health", "ore_mined_callback"]

    typeToHealth = {OreType.IRON: 1000, OreType.COPPER: 800, OreType.GOLD: 500, OreType.VULCAN: 200, OreType.CRYSTAL: 300} 

    # TODO : add the removing of health points
    def __init__(self, type, coords, ore_mined_callback, orientation = Orientation.RANDOM) -> None:
        super().__init__(StructureType.ORE, coords, [Point(-1, -1), Point(0, -1), Point(-2, 0), Point(-1, 0), Point(0, 0), Point(1, 0), Point(-2, 1), Point(-1, 1), Point(0, 1), Point(1, 1), Point(-1, 2)], orientation)
        self.type = type
        self.health = self.typeToHealth[type]
        self.ore_mined_callback = ore_mined_callback

    def mine(self, quantity):
        self.health -= quantity
        if self.health <= 0:
            self.ore_mined_callback(self)
            return True
        return False

class BuildingType(Enum):
    BASE_CAMP = 1
    PANTRY = 2
    FARM = 3
    MINER_CAMP = 4

class BuildingState(Enum):
    PLACED = 0
    BUILDING = 1
    BUILT = 2

# TODO: maybe create a class 'TypedStructure' inheriting of 'Structure' to add the type attribute instead of adding it to every subclass of Structure?
class Building(Structure):
    __slots__ = ["type", "costs", "health", "building_duration", "building_time", "workers", "state", "player"]

    def __init__(self, costs, health, building_duration, type, coords, points, player, orientation=Orientation.RANDOM) -> None:
        super().__init__(StructureType.BUILDING, coords, points, orientation)
        self.costs = costs
        self.health = health
        self.building_duration = building_duration
        self.building_time = 0
        self.workers = 0
        self.type = type
        self.player = player
        self.state = BuildingState.PLACED

    def addWorkers(self, workers_number):
        self.workers += workers_number

    def update(self, duration):
        # Should be called BEFORE adding or removing workers
        if self.state != BuildingState.BUILT:
            old_time = self.building_time
            self.building_time += duration * self.workers

            if self.building_time != 0 and old_time == 0:
                self.state = BuildingState.BUILDING

            if self.building_duration < self.building_time:
                self.state = BuildingState.BUILT

        return self.state

class BaseCamp(Building):
    def __init__(self, coords, player, orientation=Orientation.RANDOM) -> None:
        # TODO: add costs when the ressource system is ready
        super().__init__(None, 2000, 0, BuildingType.BASE_CAMP, coords, Rectangle(-2, -2, 2, 2).toPointList(), player, orientation)
        
class Pantry(Building):
    def __init__(self, coords, player, orientation=Orientation.RANDOM) -> None:
        # TODO: add costs when the ressource system is ready
        super().__init__(None, 550, 1 * 60, BuildingType.PANTRY, coords, Rectangle(-1, -1, 1, 1).toPointList(), player, orientation)

class Farm(Building):
    __slots__ = ["food"]

    def __init__(self, coords, player, orientation=Orientation.RANDOM) -> None:
        # TODO: add costs when the ressource system is ready
        super().__init__(None, 300, 0.5 * 60, BuildingType.FARM, coords, Rectangle(-1, -1, 1, 1).toPointList(), player, orientation)

    def update(self, duration):
        state = super().update(duration)
        if state == BuildingState.BUILT:
            self.player.add_ressource(RessourceType.FOOD, duration * 0.1)
        
        return state
    
class MinerCamp(Building):
    def __init__(self, coords, player, orientation=Orientation.RANDOM) -> None:
        # TODO: add costs when the ressource system is ready
        super().__init__(None, 550, 0, BuildingType.MINER_CAMP, coords, Rectangle(-1, -1, 1, 1).toPointList(), player, orientation)