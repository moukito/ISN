from enum import Enum
from math import inf
from random import uniform

from model.Entity import Entity
from model.Structures import StructureType, BuildingType, BuildingState, OreType, oreToRessourceType
from model.Ressource import RessourceType
from model.Geometry import Point
from model.Map import Map
from model.AStar import AStar
from model.Upgrades import Upgrades
from model.HumanType import HumanType
from model.Tools import Directions

class HumanState(Enum):
    IDLE = 0
    MOVING = 1
    WORKING = 2

class HumanWork(Enum):
    IDLE = 0
    GATHERING = 1
    HUNTING = 2
    BUILDING = 3
    FIGHTING = 4

class GatherState(Enum):
    GATHERING = 1
    DEPOSITING = 2

class Human(Entity):
    __slots__ = ["name", "current_location", "target_location", "building_location", "path", "resource_capacity", "gathering_speed", "ressource_type", "deposit_speed", "speed", "progression", "going_to_work", "going_to_target", "going_to_deposit", "state", "work", "gather_state", "map", "player"]

    CELL_CENTER = Point(Map.CELL_SIZE, Map.CELL_SIZE) // 2

    def __init__(self, health, type, capacity, gathering_speed, speed, map, location, player):
        super().__init__(health, {})
        self.type = type
        self.current_location = location - location % Map.CELL_SIZE + Human.CELL_CENTER
        self.target_location = None
        self.building_location = None
        self.path = None
        self.resource_capacity = capacity
        self.gathering_speed = gathering_speed
        self.ressource_type = None
        self.deposit_speed = 2
        self.speed = speed
        self.progression = 0
        self.going_to_work = False
        self.going_to_target = False
        self.going_to_deposit = False
        self.state = HumanState.IDLE
        self.work = HumanWork.IDLE
        self.gather_state = GatherState.GATHERING
        self.map = map
        self.player = player
        self.orientation = Directions.BOTTOM

    def find_nearest_building(self, building_types):
        buildings = []
        for building_type in building_types:
            actual_buildings = self.map.building_type.get(building_type, None)
            if actual_buildings is not None:
                for building in actual_buildings:
                    if building.state != BuildingState.PLACED and building.state != BuildingState.BUILDING:
                        buildings.append(building)

        nearest_building = None
        min_path = None
        min_distance = +inf
        for building in buildings:
            path = AStar(self.current_location // Map.CELL_SIZE, building.coords, self.map)
            distance = +inf if path is None else len(path)
            if distance < min_distance:
                min_distance = distance
                nearest_building = building
                min_path = path

        return nearest_building.coords, min_path

    def move(self, duration):
        old_progression = self.progression
        self.progression += duration * self.speed
        path_start = 0
        path_end = 0
        diff = None

        if self.progression < len(self.path) - 1:
            self.progression = min(self.progression, len(self.path) - 1)
            path_start = int(self.progression)
            path_end = path_start + 1
            diff = (self.path[path_end] - self.path[path_start])
            self.current_location = self.path[path_start] + diff * (self.progression % 1)
        else:
            self.current_location = self.path[-1]
            self.progression = len(self.path) - 1
            if len(self.path) > 1:
                diff = (self.path[-2] - self.path[-1])
        
        if diff is not None:
            if diff.x > 0:
                self.orientation = Directions.RIGHT
            elif diff.x < 0:
                self.orientation = Directions.LEFT
            else:
                if diff.y > 0:
                    self.orientation = Directions.BOTTOM
                elif diff.y < 0:
                    self.orientation = Directions.TOP

        return 0 if self.progression < len(self.path) - 1 else duration - (len(self.path) - 1 - old_progression) / self.speed
    
    def get_ressource_count(self, ressources):
        count = 0
        for ressource in ressources.values():
            count += ressource
        return count

    def gather_resources(self, duration):
        if self.ressources.get(self.ressource_type, None) is None:
            self.ressources[self.ressource_type] = 0
        old_ressources = self.ressources
        capacity = self.resource_capacity - self.get_ressource_count(old_ressources)

        gathering_speed = self.gathering_speed
        if self.ressource_type == RessourceType.FOOD:
            gathering_speed *= Upgrades.FOOD_MULTIPLIER
        elif self.ressource_type in [RessourceType.STONE, RessourceType.IRON, RessourceType.COPPER, RessourceType.GOLD, RessourceType.CRYSTAL, RessourceType.VULCAN]:
            gathering_speed *= Upgrades.MINING_MULTIPLIER
        if (self.type == HumanType.LUMBERJACK and self.ressource_type == RessourceType.WOOD
            or self.type == HumanType.FARMER and self.ressource_type == RessourceType.FOOD
            or self.type == HumanType.MINER and self.ressource_type in [RessourceType.STONE, RessourceType.IRON, RessourceType.COPPER, RessourceType.GOLD, RessourceType.CRYSTAL, RessourceType.VULCAN]):
            gathering_speed *= 2

        self.ressources[self.ressource_type] += min(duration * gathering_speed, capacity)
        duration_left = 0 if self.get_ressource_count(self.ressources) < self.resource_capacity else duration - capacity / gathering_speed
        
        struct =  self.map.occupied_coords.get(self.target_location, None)
        if struct is None or struct.structure_type == StructureType.ORE or struct.structure_type == StructureType.TREE:
            struct_destroyed = False
            if struct is not None:
                if struct.structure_type == StructureType.ORE:
                    struct_destroyed = struct.mine((duration - duration_left) * self.gathering_speed)
                else:
                    struct_destroyed = struct.chop_down((duration - duration_left) * self.gathering_speed)
                    
            if struct is None or struct_destroyed:
                self.gather_state = GatherState.DEPOSITING
                self.going_to_target = False
                self.go_to_location(self.building_location)
            
        return duration_left

    def deposit_resources(self, duration):
        total_deposit = 0
        for ressource, quantity in self.ressources.items():
            deposit = min(duration * self.deposit_speed, quantity)
            self.player.add_ressource(ressource, deposit)
            self.ressources[ressource] -= deposit
            if quantity > deposit:
                total_deposit += deposit
                break
            else:
                total_deposit += quantity
                duration -= deposit / self.deposit_speed
                self.ressources[ressource] = 0
        
        return 0 if self.get_ressource_count(self.ressources) > 0 else duration - total_deposit / self.deposit_speed

    def set_target_location(self, location):
        self.target_location = location
        self.go_to_location(self.target_location)

    def create_path(self, location):
        self.path = AStar(self.current_location // Map.CELL_SIZE, location, self.map)
        if len(self.path) > 1:
            self.path[0] = self.current_location
        self.path[-1] = self.path[-1] + Point(uniform(-1, 1), uniform(-1, 1)) * Map.CELL_SIZE
        
    def go_to_location(self, location):
        if self.work == HumanWork.BUILDING:
            building = self.map.occupied_coords.get(self.building_location, None)
            if building is not None:
                building.addWorkers(-1)

        self.progression = 0
        struct = self.map.occupied_coords.get(location, None)
        if struct is None:
            self.state = HumanState.MOVING
            self.work = HumanWork.IDLE
        else:
            self.state = HumanState.WORKING
            self.going_to_work = True
            if struct.structure_type == StructureType.BUILDING:
                self.going_to_target = False
                if struct.state == BuildingState.PLACED or struct.state == BuildingState.BUILDING:
                    self.work = HumanWork.BUILDING
                    self.building_location = location
                else:
                    if struct.type == BuildingType.FARM:
                        self.work = HumanWork.GATHERING
                        self.gather_state = GatherState.GATHERING
                        self.ressource_type = RessourceType.FOOD
                        self.going_to_target = True
                        self.building_location, _ = self.find_nearest_building([BuildingType.BASE_CAMP, BuildingType.PANTRY])
                    else:
                        self.building_location = location
            elif struct.structure_type == StructureType.ORE and (
                    (struct.type == OreType.VULCAN or struct.type == OreType.CRYSTAL) and Upgrades.EXTRA_MATERIALS or 
                    (struct.type != OreType.VULCAN and struct.type != OreType.CRYSTAL)):
                self.work = HumanWork.GATHERING
                self.gather_state = GatherState.GATHERING
                self.ressource_type = oreToRessourceType[struct.type]
                self.going_to_target = True
                self.building_location, _ = self.find_nearest_building([BuildingType.BASE_CAMP, BuildingType.MINER_CAMP])
            elif struct.structure_type == StructureType.TREE:
                self.work = HumanWork.GATHERING
                self.gather_state = GatherState.GATHERING
                self.ressource_type = RessourceType.WOOD
                self.going_to_target = True
                self.building_location, _ = self.find_nearest_building([BuildingType.BASE_CAMP, BuildingType.LUMBER_CAMP])
        self.create_path(location)

    def update(self, duration):
        result = False
        if self.state != HumanState.IDLE:
            position = self.current_location
            if self.state == HumanState.MOVING or self.going_to_work:
                duration = self.move(duration)
                if duration > 0:
                    if self.work != HumanWork.IDLE:
                        self.going_to_work = False
                        if self.work == HumanWork.BUILDING:
                            building = self.map.occupied_coords.get(self.building_location, None)
                            if building is not None:
                                building.addWorkers(1)
                    else:
                        self.state = HumanState.IDLE
                        duration = 0
            while duration > 0:
                if self.state == HumanState.WORKING:
                    if self.going_to_deposit:
                        duration = self.move(duration)
                        if duration > 0:
                            self.going_to_deposit = False
                    elif self.work == HumanWork.GATHERING:
                        if self.gather_state == GatherState.GATHERING:
                            duration = self.gather_resources(duration)
                            if duration > 0:
                                self.going_to_deposit = True
                                self.gather_state = GatherState.DEPOSITING
                                self.going_to_target = False
                                self.go_to_location(self.building_location)
                        else:
                            duration = self.deposit_resources(duration)
                            if duration > 0:
                                self.gather_state = GatherState.GATHERING
                                self.going_to_target = True
                                self.go_to_location(self.target_location)
                            
                    elif self.work == HumanWork.BUILDING:
                        duration = 0
                    elif self.work == HumanWork.HUNTING or self.work == HumanWork.FIGHTING:
                        # TODO: When there are animals and / or the AI
                        duration = 0
                else:
                    duration = self.move(duration)
                    if duration > 0 and self.work != HumanWork.IDLE:
                        self.go_to_location(self.target_location if self.going_to_target else self.building_location)
                        self.going_to_work = False
            result = self.current_location != position
        return result
    
    def stop(self):
        self.state = HumanState.IDLE
        self.work = HumanWork.IDLE
        self.going_to_work = False
        self.going_to_target = False

class Colon(Human):
    def __init__(self, map, location, player):
        super().__init__(100, HumanType.COLON, 5, 1, 2, map, location, player)

class Miner(Human):
    def __init__(self, map, location, player):
        super().__init__(100, HumanType.MINER, 5, 1, 2, map, location, player)

class Lumberjack(Human):
    def __init__(self, map, location, player):
        super().__init__(100, HumanType.LUMBERJACK, 5, 1, 2, map, location, player)

class Farmer(Human):
    def __init__(self, map, location, player):
        super().__init__(100, HumanType.FARMER, 5, 1, 2, map, location, player)


human_type_class = {
    HumanType.COLON: Colon,
    HumanType.MINER: Miner,
    HumanType.LUMBERJACK: Lumberjack,
    HumanType.FARMER: Farmer
}

def get_human_class_from_type(human_type):
    return human_type_class[human_type]