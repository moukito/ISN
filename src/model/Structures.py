from enum import Enum
from math import inf
import random

from model.Geometry import Point, Rectangle
from model.Ressource import RessourceType
from model.Player import Player
from model.Upgrades import Technologies
from model.HumanType import HumanType
from model.Player import Player

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
    __slots__ = ["sid", "structure_type", "coords", "points", "orientation"]

    SID = 0

    def __init__(self, structure_type, coords, points, orientation = Orientation.RANDOM) -> None:
        Structure.SID += 1
        self.sid = Structure.SID
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
    HUNTER_CAMP = 6
    SOLDIER_CAMP = 7

class BuildingState(Enum):
    PLACED = 0
    BUILDING = 1
    BUILT = 2

class Building(TypedStructure):
    __slots__ = ["costs", "health", "building_duration", "building_time", "workers", "state", "player", "destroy_callback", "human_death_callback", "upper_left", "rect_size", "gamevue", "buttons"]

    def __init__(self, costs, health, building_duration, type, coords, points, player, destroy_callback, human_death_callback, orientation=Orientation.RANDOM) -> None:
        super().__init__(type, StructureType.BUILDING, coords, points, orientation)
        self.costs = costs
        self.building_duration = building_duration
        self.building_time = 0
        self.workers = 0
        self.player = player
        self.health = health * self.player.upgrades.BUILDING_HEALTH_MULTIPLIER
        self.destroy_callback = destroy_callback
        self.human_death_callback = human_death_callback
        self.state = BuildingState.PLACED
        self.gamevue = None
        self.buttons = {}

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
        self.upper_left = Point(min.x, min.y)
        self.rect_size = Point(max.x - min.x + 1, max.y - min.y + 1)

    def destroy(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.destroy_callback(self)
    
    def get_buttons(self, gamevue):
        self.gamevue = gamevue
        return self.buttons

    def addWorkers(self, workers_number):
        self.workers += workers_number

    def update(self, duration):
        # Should be called BEFORE adding or removing workers
        need_render = False
        if self.state != BuildingState.BUILT:
            need_render = True
            old_time = self.building_time
            self.building_time += duration * self.workers * self.player.upgrades.BUILDING_TIME_MULTIPLIER

            if self.building_time != 0 and old_time == 0:
                self.state = BuildingState.BUILDING

            if self.building_duration < self.building_time:
                self.state = BuildingState.BUILT

        return need_render

class BaseCamp(Building):
    def __init__(self, coords, player, destroy_callback, human_death_callback, orientation=Orientation.RANDOM) -> None:
        super().__init__(None, 2000, 0, BuildingType.BASE_CAMP, coords, Rectangle(-2, -2, 2, 2).toPointList(), player, destroy_callback, human_death_callback, Orientation.NORTH)
        self.state = BuildingState.BUILT
        self.building_time = self.building_duration
        self.buttons = {
            Point(0, 0): ({RessourceType.FOOD: 150}, HumanType.COLON, self.spawn_colon)
        }
    
    def get_buttons(self, gamevue):
        self.gamevue = gamevue
        buttons = self.buttons.copy()
        if self.player.upgrades.BUILDING_HEALTH_MULTIPLIER != 2:
            buttons[Point(1, 0)] = ({RessourceType.FOOD: 400, RessourceType.WOOD: 300, RessourceType.STONE: 300}, Technologies.BUILDING_HEALTH, self.technology_building_health)
        if self.player.upgrades.BUILDING_TIME_MULTIPLIER != 2:
            buttons[Point(1, 1)] = ({RessourceType.WOOD: 500, RessourceType.STONE: 600, RessourceType.CRYSTAL: 500}, Technologies.BUILDING_TIME, self.technology_building_time)
        if not self.player.upgrades.EXTRA_MATERIALS:
            buttons[Point(1, 2)] = ({RessourceType.STONE: 400, RessourceType.IRON: 400, RessourceType.GOLD: 300}, Technologies.EXTRA_MATERIALS, self.technology_extra_materials)
        return buttons
    
    def spawn_colon(self):
        if self.player.get_ressource(RessourceType.FOOD) >= 150:
            self.player.add_ressource(RessourceType.FOOD, -150)
            self.gamevue.add_human(HumanType.COLON, self.coords + random.choice(Rectangle(-2, -2, 2, 2).toPointList()) + Point(1, 1) * random.uniform(-0.5, 0.5))

    def technology_building_time(self):
        if self.player.get_ressource(RessourceType.FOOD) >= 400 and self.player.get_ressource(RessourceType.WOOD) >= 300 and self.player.get_ressource(RessourceType.STONE) >= 300:
            self.player.add_ressource(RessourceType.FOOD, -400)
            self.player.add_ressource(RessourceType.WOOD, -300)
            self.player.add_ressource(RessourceType.STONE, -300)
            self.player.upgrades.BUILDING_TIME_MULTIPLIER = 2

    def technology_building_health(self):
        if self.player.get_ressource(RessourceType.WOOD) >= 500 and self.player.get_ressource(RessourceType.STONE) >= 600 and self.player.get_ressource(RessourceType.CRYSTAL) >= 500:
            self.player.add_ressource(RessourceType.WOOD, -500)
            self.player.add_ressource(RessourceType.STONE, -600)
            self.player.add_ressource(RessourceType.CRYSTAL, -500)
            self.player.upgrades.BUILDING_HEALTH_MULTIPLIER = 2
            for building in self.gamevue.map.buildings:
                if building.player == self.player:
                    building.health *= 2

    def technology_extra_materials(self):
        if self.player.get_ressource(RessourceType.STONE) >= 400 and self.player.get_ressource(RessourceType.IRON) >= 400 and self.player.get_ressource(RessourceType.GOLD) >= 300:
            self.player.add_ressource(RessourceType.STONE, -400)
            self.player.add_ressource(RessourceType.IRON, -400)
            self.player.add_ressource(RessourceType.GOLD, -300)
            self.player.upgrades.EXTRA_MATERIALS = True
        
class Pantry(Building):
    def __init__(self, coords, player, destroy_callback, human_death_callback, orientation=Orientation.RANDOM) -> None:
        super().__init__({RessourceType.WOOD: 75, RessourceType.STONE: 25}, 550, 2.5 * 60, BuildingType.PANTRY, coords, Rectangle(-1, -1, 1, 1).toPointList(), player, destroy_callback, human_death_callback, orientation)
        self.buttons = {
            Point(0, 0): ({RessourceType.FOOD: 200}, HumanType.FARMER, self.spawn_farmer)
        }
    
    def get_buttons(self, gamevue):
        self.gamevue = gamevue
        buttons = self.buttons.copy()
        if self.player.upgrades.FOOD_MULTIPLIER != 2:
            buttons[Point(1, 0)] = ({RessourceType.FOOD: 600, RessourceType.WOOD: 300, RessourceType.IRON: 300}, Technologies.AGRICULTURE, self.technology_agriculture)
        return buttons
    
    def spawn_farmer(self):
        if self.player.get_ressource(RessourceType.FOOD) >= 200:
            self.player.add_ressource(RessourceType.FOOD, -200)
            self.gamevue.add_human(HumanType.FARMER, self.coords + random.choice(Rectangle(-1, -1, 1, 1).toPointList()) + Point(1, 1) * random.uniform(-0.5, 0.5))

    def technology_agriculture(self):
        if self.player.get_ressource(RessourceType.FOOD) >= 600 and self.player.get_ressource(RessourceType.WOOD) >= 300 and self.player.get_ressource(RessourceType.IRON) >= 300:
            self.player.add_ressource(RessourceType.FOOD, -600)
            self.player.add_ressource(RessourceType.WOOD, -300)
            self.player.add_ressource(RessourceType.IRON, -300)
            self.player.upgrades.FOOD_MULTIPLIER = 2

class Farm(Building):
    def __init__(self, coords, player, destroy_callback, human_death_callback, orientation=Orientation.RANDOM) -> None:
        super().__init__({RessourceType.WOOD: 50}, 300, 1 * 60, BuildingType.FARM, coords, Rectangle(-1, -1, 1, 1).toPointList(), player, destroy_callback, human_death_callback, orientation)
    
class MinerCamp(Building):
    def __init__(self, coords, player, destroy_callback, human_death_callback, orientation=Orientation.RANDOM) -> None:
        super().__init__({RessourceType.WOOD: 75, RessourceType.STONE: 25, RessourceType.IRON: 25}, 550, 1 * 60, BuildingType.MINER_CAMP, coords, Rectangle(-1, -1, 1, 1).toPointList(), player, destroy_callback, human_death_callback, orientation)
        self.buttons = {
            Point(0, 0): ({RessourceType.FOOD: 150, RessourceType.COPPER: 50}, HumanType.MINER, self.spawn_miner)
        }
    
    def get_buttons(self, gamevue):
        self.gamevue = gamevue
        buttons = self.buttons.copy()
        if self.player.upgrades.MINING_MULTIPLIER != 2:
            buttons[Point(1, 0)] = ({RessourceType.IRON: 600, RessourceType.COPPER: 400, RessourceType.VULCAN: 200}, Technologies.MINING, self.technology_mining)
        return buttons
    
    def spawn_miner(self):
        if self.player.get_ressource(RessourceType.FOOD) >= 150 and self.player.get_ressource(RessourceType.COPPER) >= 50:
            self.player.add_ressource(RessourceType.FOOD, -150)
            self.player.add_ressource(RessourceType.COPPER, -50)
            self.gamevue.add_human(HumanType.MINER, self.coords + random.choice(Rectangle(-1, -1, 1, 1).toPointList()) + Point(1, 1) * random.uniform(-0.5, 0.5))

    def technology_mining(self):
        if self.player.get_ressource(RessourceType.IRON) >= 600 and self.player.get_ressource(RessourceType.COPPER) >= 400 and self.player.get_ressource(RessourceType.VULCAN) >= 200:
            self.player.add_ressource(RessourceType.IRON, -600)
            self.player.add_ressource(RessourceType.COPPER, -400)
            self.player.add_ressource(RessourceType.VULCAN, -200)
            self.player.upgrades.MINING_MULTIPLIER = 2
            
class LumberCamp(Building) :
    def __init__(self, coords, player, destroy_callback, human_death_callback, orientation=Orientation.RANDOM) -> None : 
        super().__init__({RessourceType.WOOD: 100, RessourceType.STONE: 25}, 550, 1 * 60, BuildingType.LUMBER_CAMP, coords, Rectangle(-1,-1,1,1).toPointList(), player, destroy_callback, human_death_callback, orientation)
        self.buttons = {
            Point(0, 0): ({RessourceType.FOOD: 150, RessourceType.WOOD: 50}, HumanType.LUMBERJACK, self.spawn_lumberjack)
        }
    
    def get_buttons(self, gamevue):
        self.gamevue = gamevue
        buttons = self.buttons.copy()
        if self.player.upgrades.WOOD_MULTIPLIER != 2:
            buttons[Point(1, 0)] = ({RessourceType.WOOD: 600, RessourceType.IRON: 300, RessourceType.FOOD: 200}, Technologies.FORESTRY, self.technology_forestry)
        return buttons
    
    def spawn_lumberjack(self):
        if self.player.get_ressource(RessourceType.FOOD) >= 150 and self.player.get_ressource(RessourceType.WOOD) >= 50:
            self.player.add_ressource(RessourceType.FOOD, -150)
            self.player.add_ressource(RessourceType.WOOD, -50)
            self.gamevue.add_human(HumanType.LUMBERJACK, self.coords + random.choice(Rectangle(-1, -1, 1, 1).toPointList()) + Point(1, 1) * random.uniform(-0.5, 0.5))

    def technology_forestry(self):
        if self.player.get_ressource(RessourceType.WOOD) >= 600 and self.player.get_ressource(RessourceType.IRON) >= 300 and self.player.get_ressource(RessourceType.FOOD) >= 200:
            self.player.add_ressource(RessourceType.WOOD, -600)
            self.player.add_ressource(RessourceType.IRON, -300)
            self.player.add_ressource(RessourceType.FOOD, -200)
            self.player.upgrades.WOOD_MULTIPLIER = 2

class HunterCamp(Building) :
    def __init__(self, coords, player, destroy_callback, human_death_callback, orientation=Orientation.RANDOM) -> None :
        super().__init__({RessourceType.WOOD: 50, RessourceType.STONE: 25, RessourceType.FOOD: 25}, 550, 1 * 60, BuildingType.HUNTER_CAMP, coords, Rectangle(-1,-1,1,1).toPointList(), player, destroy_callback, human_death_callback, orientation)
        self.buttons = {
            Point(0, 0): ({RessourceType.FOOD: 200}, HumanType.HUNTER, self.spawn_hunter)
        }
    
    def get_buttons(self, gamevue):
        self.gamevue = gamevue
        buttons = self.buttons.copy()
        if self.player.upgrades.HUNT_MULTIPLIER != 2:
            buttons[Point(1, 0)] = ({RessourceType.WOOD: 400, RessourceType.COPPER: 400, RessourceType.FOOD: 200}, Technologies.HUNT, self.technology_hunt)
        return buttons
    
    def spawn_hunter(self):
        if self.player.get_ressource(RessourceType.FOOD) >= 200:
            self.player.add_ressource(RessourceType.FOOD, -200)
            self.gamevue.add_human(HumanType.HUNTER, self.coords + random.choice(Rectangle(-1, -1, 1, 1).toPointList()) + Point(1, 1) * random.uniform(-0.5, 0.5))

    def technology_hunt(self):
        if self.player.get_ressource(RessourceType.WOOD) >= 400 and self.player.get_ressource(RessourceType.COPPER) >= 400 and self.player.get_ressource(RessourceType.FOOD) >= 200:
            self.player.add_ressource(RessourceType.WOOD, -400)
            self.player.add_ressource(RessourceType.COPPER, -400)
            self.player.add_ressource(RessourceType.FOOD, -200)
            self.player.upgrades.HUNT_MULTIPLIER = 2

class SoldierCamp(Building) :
    def __init__(self, coords, player, destroy_callback, human_death_callback, orientation=Orientation.RANDOM) -> None :
        super().__init__({RessourceType.WOOD: 50, RessourceType.STONE: 25, RessourceType.IRON: 50}, 750, 1 * 60, BuildingType.SOLDIER_CAMP, coords, Rectangle(-1,-1,1,1).toPointList(), player, destroy_callback, human_death_callback, orientation)
        self.buttons = {
            Point(0, 0): ({RessourceType.FOOD: 150, RessourceType.IRON: 50}, HumanType.SOLDIER, self.spawn_soldier)
        }
    
    def get_buttons(self, gamevue):
        self.gamevue = gamevue
        buttons = self.buttons.copy()
        if self.player.upgrades.HUNT_MULTIPLIER != 2:
            buttons[Point(1, 0)] = ({RessourceType.WOOD: 400, RessourceType.COPPER: 400, RessourceType.FOOD: 200}, Technologies.HUNT, self.technology_combat)
        return buttons
    
    def spawn_soldier(self):
        if self.player.get_ressource(RessourceType.FOOD) >= 150 and self.player.get_ressource(RessourceType.IRON) >= 50:
            self.player.add_ressource(RessourceType.FOOD, -150)
            self.player.add_ressource(RessourceType.IRON, -50)
            self.gamevue.add_human(HumanType.SOLDIER, self.coords + random.choice(Rectangle(-1, -1, 1, 1).toPointList()) + Point(1, 1) * random.uniform(-0.5, 0.5))

    def technology_combat(self):
        if self.player.get_ressource(RessourceType.WOOD) >= 400 and self.player.get_ressource(RessourceType.COPPER) >= 400 and self.player.get_ressource(RessourceType.FOOD) >= 200:
            self.player.add_ressource(RessourceType.WOOD, -400)
            self.player.add_ressource(RessourceType.COPPER, -400)
            self.player.add_ressource(RessourceType.FOOD, -200)
            self.player.upgrades.COMBAT_MULTIPLIER = 2

typeToClass = {
    BuildingType.BASE_CAMP: BaseCamp,
    BuildingType.PANTRY: Pantry,
    BuildingType.FARM: Farm,
    BuildingType.MINER_CAMP: MinerCamp,
    BuildingType.LUMBER_CAMP: LumberCamp,
    BuildingType.HUNTER_CAMP: HunterCamp,
    BuildingType.SOLDIER_CAMP: SoldierCamp
}

def get_struct_class_from_type(structure_type):
    return typeToClass[structure_type]
