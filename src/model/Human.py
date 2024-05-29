from enum import Enum
from math import inf

from model.Entity import Entity
from model.Structures import StructureType, BuildingType, oreToRessourceType
from model.Ressource import RessourceType
from model.Geometry import Point
from model.Map import Map
from model.AStar import AStar
from model.Upgrades import HumanType

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
    __slots__ = ["name", "current_location", "target_location", "building_location", "path", "resource_capacity", "gathering_speed", "ressource_type", "deposit_speed", "speed", "progression", "going_to_work", "going_to_target", "state", "work", "gather_state", "map", "player"]

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
        self.state = HumanState.IDLE
        self.work = HumanWork.IDLE
        self.gather_state = GatherState.GATHERING
        self.map = map
        self.player = player

    def find_nearest_building(self, building_types):
        buildings = []
        for building_type in building_types:
            buildings += self.map.building_type.get(building_type, [])

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
        if self.progression < len(self.path) - 1:
            self.progression = min(self.progression, len(self.path) - 1)
            path_start = int(self.progression // 1)
            path_end = path_start + 1
            diff = (self.path[path_end] - self.path[path_start])
            self.current_location = self.path[path_start] + diff * (self.progression % 1)
        else:
            self.current_location = self.path[-1]
            self.progression = len(self.path) - 1
        return 0 if self.progression < len(self.path) - 1 else duration - (len(self.path) - 1 - old_progression) / self.speed

    def gather_resources(self, duration):
        if self.ressources.get(self.ressource_type, None) is None:
            self.ressources[self.ressource_type] = 0
        old_ressources = self.ressources[self.ressource_type]
        self.ressources[self.ressource_type] = min(self.ressources[self.ressource_type] + duration * self.gathering_speed, self.resource_capacity)
        duration_left = 0 if self.ressources[self.ressource_type] < self.resource_capacity else duration - (self.resource_capacity - old_ressources) / self.gathering_speed
        
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
        deposit = min(duration * self.deposit_speed, self.ressources[self.ressource_type])
        self.player.add_ressource(self.ressource_type, deposit)
        self.ressources[self.ressource_type] -= deposit
        return 0 if self.ressources[self.ressource_type] > 0 else duration - deposit / self.deposit_speed

    def set_target_location(self, location):
        self.target_location = location
        self.go_to_location(self.target_location)

    def go_to_location(self, location):
        # TODO: Add a small random offset to be able to distinguish multiple humans going to the same location 
        # TODO: Fix the human not going to the nearest building
        self.progression = 0
        struct = self.map.occupied_coords.get(location, None)
        if struct is None:
            self.state = HumanState.MOVING
            self.work = HumanWork.IDLE
            self.path = AStar(self.current_location // Map.CELL_SIZE, location, self.map)
        else:
            self.state = HumanState.WORKING
            self.going_to_work = True
            if struct.structure_type == StructureType.BUILDING:
                self.going_to_target = False
                if struct.type == BuildingType.FARM:
                    self.work = HumanWork.GATHERING
                    self.ressource_type = RessourceType.FOOD
                    self.going_to_target = True
                    self.building_location, _ = self.find_nearest_building([BuildingType.BASE_CAMP, BuildingType.FARM])
                    self.path = AStar(self.current_location // Map.CELL_SIZE, location, self.map)
                    if len(self.path) > 1:
                        self.path[0] = self.current_location
                else:
                    self.building_location = location
                    self.path = AStar(self.current_location // Map.CELL_SIZE, location, self.map)
                    if len(self.path) > 1:
                        self.path[0] = self.current_location
            elif struct.structure_type == StructureType.ORE:
                self.work = HumanWork.GATHERING
                self.ressource_type = oreToRessourceType[struct.type]
                self.going_to_target = True
                self.building_location, _ = self.find_nearest_building([BuildingType.BASE_CAMP, BuildingType.MINER_CAMP])
                self.path = AStar(self.current_location // Map.CELL_SIZE, location, self.map)
                if len(self.path) > 1:
                    self.path[0] = self.current_location
            elif struct.structure_type == StructureType.TREE:
                self.work = HumanWork.GATHERING
                self.ressource_type = RessourceType.WOOD
                self.going_to_target = True
                self.building_location, _ = self.find_nearest_building([BuildingType.BASE_CAMP, BuildingType.LUMBER_CAMP])
                self.path = AStar(self.current_location // Map.CELL_SIZE, location, self.map)
                if len(self.path) > 1:
                    self.path[0] = self.current_location

    def update(self, duration):
        result = False
        if self.state != HumanState.IDLE:
            position = self.current_location
            if self.state == HumanState.MOVING or self.going_to_work:
                duration = self.move(duration)
                if duration > 0:
                    if self.work != HumanWork.IDLE:
                        self.going_to_work = False
                    else:
                        self.state = HumanState.IDLE
                        duration = 0
            while duration > 0:
                if self.state == HumanState.WORKING:
                    if self.work == HumanWork.GATHERING:
                        if self.gather_state == GatherState.GATHERING:
                            duration = self.gather_resources(duration)
                            if duration > 0:
                                self.gather_state = GatherState.DEPOSITING
                                self.going_to_target = False
                                self.go_to_location(self.building_location)
                        else:
                            # TODO : Fix the deposit of 5 ressources (sometimes not putting 5 ressources in the inventory)
                            duration = self.deposit_resources(duration)
                            if duration > 0:
                                self.gather_state = GatherState.GATHERING
                                self.going_to_target = True
                                self.go_to_location(self.target_location)
                            
                    elif self.work == HumanWork.BUILDING:
                        # Kind of idling ?
                        duration = 0
                    elif self.work == HumanWork.HUNTING or self.work == HumanWork.FIGHTING:
                        # TODO
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