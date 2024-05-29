from enum import Enum
from math import inf
import random

from model.Geometry import Point, Rectangle
from model.Ressource import RessourceType
from model.Player import Player
from model.Upgrades import Technologies, HumanType

class StructureType(Enum):
    TREE = 1
    ORE = 2
    BUILDING = 3

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
    
class Tree(Structure):
    __slots__ = ["health", "tree_choped_callback"]

    def __init__(self, coords, tree_choped_callback, orientation = Orientation.RANDOM) -> None:
        super().__init__(StructureType.TREE, coords, Rectangle(-1, -1, 1, 1).toPointList(), orientation)
        self.health = 200
        self.tree_choped_callback = tree_choped_callback

    def chop_down(self, quantity):
        self.health -= quantity
        if self.health <= 0:
            self.tree_choped_callback(self)
            return True
        return False
    
class TypedStructure(Structure):
    __slots__ = ["type"]

    def __init__(self, type, structure_type, coords, points, orientation = Orientation.RANDOM) -> None:
        super().__init__(structure_type, coords, points, orientation)
        self.type = type

class OreType(Enum):
    STONE = 1
    IRON = 2
    COPPER = 3
    GOLD = 4
    VULCAN = 5
    CRYSTAL = 6

oreToRessourceType = {
    OreType.STONE: RessourceType.STONE,
    OreType.IRON: RessourceType.IRON,
    OreType.COPPER: RessourceType.COPPER,
    OreType.GOLD: RessourceType.GOLD,
    OreType.VULCAN: RessourceType.VULCAN,
    OreType.CRYSTAL: RessourceType.CRYSTAL
}

class Ore(TypedStructure):
    __slots__ = ["health", "ore_mined_callback"]

    typeToHealth = {OreType.STONE: 500, OreType.IRON: 1000, OreType.COPPER: 800, OreType.GOLD: 500, OreType.VULCAN: 200, OreType.CRYSTAL: 300} 

    def __init__(self, type, coords, ore_mined_callback, orientation = Orientation.RANDOM) -> None:
        super().__init__(type, StructureType.ORE, coords, [Point(-1, -1), Point(0, -1), Point(-2, 0), Point(-1, 0), Point(0, 0), Point(1, 0), Point(-2, 1), Point(-1, 1), Point(0, 1), Point(1, 1), Point(-1, 2)], orientation)
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
    LUMBER_CAMP = 4
    MINER_CAMP = 5

class BuildingState(Enum):
    PLACED = 0
    BUILDING = 1
    BUILT = 2

class Building(TypedStructure):
    __slots__ = ["costs", "health", "building_duration", "building_time", "workers", "state", "player", "upper_left", "rect_size", "gamevue"]

    def __init__(self, costs, health, building_duration, type, coords, points, player, orientation=Orientation.RANDOM) -> None:
        super().__init__(type, StructureType.BUILDING, coords, points, orientation)
        self.costs = costs
        self.health = health
        self.building_duration = building_duration
        self.building_time = 0
        self.workers = 0
        self.player = player
        self.state = BuildingState.PLACED
        self.gamevue = None

        min = Point(+inf, +inf)
        max = Point(-inf, -inf)
        self.upper_left = Point(+inf, +inf)
        for point in points:
            if point.x < min.x:
                min.x = point.x
            elif point.x > max.x:
                max.x = point.x
            if point.y < min.y:
                min.y = point.y
            elif point.y > max.y:
                max.y = point.y
        # TODO: Maybe put that in a class attribute (instead of doing it for each building) 
        self.upper_left = Point(min.x, min.y)
        self.rect_size = Point(max.x - min.x + 1, max.y - min.y + 1)


    def addWorkers(self, workers_number):
        self.workers += workers_number

    def update(self, duration):
        # Should be called BEFORE adding or removing workers
        if self.state != BuildingState.BUILT:
            old_time = self.building_time
            self.building_time += duration * self.workers

            if self.building_time != 0 and old_time == 0:
                self.state = BuildingState.BUILDING
                # TODO : add a progression bar over the building

            if self.building_duration < self.building_time:
                self.state = BuildingState.BUILT

        return self.state
    
    def get_buttons(self, gamevue):
        return None

# TODO: remove the technology buttons when the technology is unlocked

class BaseCamp(Building):
    def __init__(self, coords, player) -> None:
        super().__init__(None, 2000, 0, BuildingType.BASE_CAMP, coords, Rectangle(-2, -2, 2, 2).toPointList(), player, Orientation.NORTH)

    def get_buttons(self, gamevue):
        self.gamevue = gamevue
        return {
            Point(0, 0): ({RessourceType.FOOD: 150}, HumanType.COLON, self.spawn_colon),
            Point(1, 0): ({RessourceType.FOOD: 400, RessourceType.WOOD: 300, RessourceType.STONE: 300}, Technologies.BUILDING_HEALTH, None), #TODO: Add a callback
            Point(1, 1): ({RessourceType.WOOD: 500, RessourceType.STONE: 600, RessourceType.CRYSTAL: 500}, Technologies.BUILDING_TIME, None), #TODO: Add a callback
        }
    
    def spawn_colon(self):
        if self.player.get_ressource(RessourceType.FOOD) >= 150:
            self.player.add_ressource(RessourceType.FOOD, -150)
            self.gamevue.add_human(HumanType.COLON, self.coords + random.choice(Rectangle(-2, -2, 2, 2).toPointList()) + Point(1, 1) * random.uniform(-0.5, 0.5))
        
class Pantry(Building):
    def __init__(self, coords, player, orientation=Orientation.RANDOM) -> None:
        super().__init__({RessourceType.WOOD: 75, RessourceType.STONE: 25}, 550, 1 * 60, BuildingType.PANTRY, coords, Rectangle(-1, -1, 1, 1).toPointList(), player, orientation)

    def get_buttons(self, gamevue):
        self.gamevue = gamevue
        return {
            Point(0, 0): ({RessourceType.FOOD: 200}, HumanType.FARMER, self.spawn_farmer),
            Point(1, 0): ({RessourceType.FOOD: 600, RessourceType.WOOD: 300, RessourceType.IRON: 300}, Technologies.AGRICULTURE, None), #TODO: Add a callback
        }
    
    def spawn_farmer(self):
        if self.player.get_ressource(RessourceType.FOOD) >= 200:
            self.player.add_ressource(RessourceType.FOOD, -200)
            self.gamevue.add_human(HumanType.FARMER, self.coords + random.choice(Rectangle(-1, -1, 1, 1).toPointList()) + Point(1, 1) * random.uniform(-0.5, 0.5))

class Farm(Building):
    __slots__ = ["food"]

    def __init__(self, coords, player, orientation=Orientation.RANDOM) -> None:
        super().__init__({RessourceType.WOOD: 50}, 300, 0.5 * 60, BuildingType.FARM, coords, Rectangle(-1, -1, 1, 1).toPointList(), player, orientation)

    def update(self, duration):
        state = super().update(duration)
        if state == BuildingState.BUILT:
            self.player.add_ressource(RessourceType.FOOD, duration * 0.1)
        
        return state
    
class MinerCamp(Building):
    def __init__(self, coords, player, orientation=Orientation.RANDOM) -> None:
        super().__init__({RessourceType.WOOD: 75, RessourceType.STONE: 25}, 550, 0, BuildingType.MINER_CAMP, coords, Rectangle(-1, -1, 1, 1).toPointList(), player, orientation)

    def get_buttons(self, gamevue):
        self.gamevue = gamevue
        return {
            Point(0, 0): ({RessourceType.FOOD: 150, RessourceType.COPPER: 50}, HumanType.FARMER, self.spawn_miner),
            Point(1, 0): ({RessourceType.IRON: 600, RessourceType.COPPER: 400, RessourceType.VULCAN: 200}, Technologies.MINING, None), #TODO: Add a callback
        }
    
    def spawn_miner(self):
        if self.player.get_ressource(RessourceType.FOOD) >= 150 and self.player.get_ressource(RessourceType.COPPER) >= 50:
            self.player.add_ressource(RessourceType.FOOD, -150)
            self.player.add_ressource(RessourceType.COPPER, -50)
            self.gamevue.add_human(HumanType.MINER, self.coords + random.choice(Rectangle(-1, -1, 1, 1).toPointList()) + Point(1, 1) * random.uniform(-0.5, 0.5))


typeToClass = {
    BuildingType.BASE_CAMP: BaseCamp,
    BuildingType.PANTRY: Pantry,
    BuildingType.FARM: Farm,
    BuildingType.MINER_CAMP: MinerCamp
}

def get_struct_class_from_type(structure_type):
    return typeToClass[structure_type]