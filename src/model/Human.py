from enum import Enum
from math import inf

from model.Entity import Entity
from model.Structures import StructureType, BuildingType
from model.Ressource import RessourceType
from model.Geometry import Point
from model.Map import Map
from model.AStar import AStar

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

class HumanType(Enum):
    COLONIST = 1
    SOLDIER = 2

class Human(Entity):
    __slots__ = ["name", "current_location", "target_location", "building_location", "path", "resource_capacity", "gathering_speed", "ressource_type", "deposit_speed", "speed", "progression", "state", "work", "gather_state", "map", "player"]

    CELL_CENTER = Point(Map.CELL_SIZE, Map.CELL_SIZE)

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
        self.deposit_speed = 100
        self.speed = speed
        self.progression = 0
        self.going_to_work = False
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

        return nearest_building, min_path

    def move(self, duration):
        old_progression = self.progression
        self.progression += duration * self.speed
        self.progression = min(self.progression, len(self.path) - 1)
        path_start = self.progression // 1
        path_end = path_end + 1
        diff = Point(self.path[path_end].position.x - self.path[path_start].position.x, self.path[path_end].position.y - self.path[path_start].position.y) * Map.CELL_SIZE
        self.current_location = Point(self.path[path_start].position.x * Map.CELL_SIZE, self.path[path_start].position.y * Map.CELL_SIZE) + diff
        return 0 if self.progression < len(self.path) - 1 else duration - (len(self.path) - 1 - old_progression) / self.speed

    def gather_resources(self, duration):
        if self.ressources.get(self.ressource_type, None):
            self.ressources[self.ressource_type] = 0
        old_ressources = self.ressources[self.ressource_type]
        self.ressources[self.ressource_type] = min(self.ressources[self.ressource_type] + duration * self.gathering_speed, self.resource_capacity)
        return 0 if self.ressources[self.ressource_type] < self.resource_capacity else duration - (self.resource_capacity - old_ressources) / self.gathering_speed

    def deposit_resources(self, duration):
        deposit = min(duration * self.deposit_speed, self.ressources[self.ressource_type])
        self.player.add_ressource(self.ressource_type, deposit)
        self.ressources[self.ressource_type] -= deposit
        return 0 if self.ressources[self.ressource_type] > 0 else duration - deposit / self.deposit_speed

    def set_target_location(self, location):
        self.target_location = location
        struct = self.map.occupied_coords.get(location, None)
        if struct is None:
            self.state = HumanState.MOVING
            self.work = HumanWork.IDLE
        else:
            self.state = HumanState.WORKING
            if struct.structure_type == StructureType.BUILDING:
                if struct.type == BuildingType.FARM:
                    self.work = HumanWork.GATHERING
                    self.ressource_type = RessourceType.FOOD
                    self.building_location = self.find_nearest_building([BuildingType.BASE_CAMP, BuildingType.FARM])
            elif struct.structure_type == StructureType.ORE:
                self.work = HumanWork.GATHERING
                self.ressource_type = struct.type
                self.building_location = self.find_nearest_building([BuildingType.BASE_CAMP, BuildingType.MINER_CAMP])


    def update(self, duration):
        if self.state != HumanState.IDLE:
            if self.state == HumanState.MOVING:
                duration = self.move(duration)
                if duration > 0 and self.work != HumanWork.IDLE:
                    self.set_target_location(self.target_location if self.going_to_work else self.building_location)
            while duration > 0:
                if self.state == HumanState.WORKING:
                    if self.work == HumanWork.GATHERING:
                        if self.gather_state == GatherState.GATHERING:
                            duration = self.gather_resources(duration)
                            if duration > 0:
                                self.gather_state = GatherState.DEPOSITING
                                self.set_target_location(self.building_location)
                        else:
                            duration = self.deposit_resources(duration)
                            if duration > 0:
                                self.gather_state = GatherState.GATHERING
                                self.set_target_location(self.target_location)
                            
                    elif self.work == HumanWork.BUILDING:
                        # Kind of idling ?
                        pass
                    elif self.work == HumanWork.HUNTING or self.work == HumanWork.FIGHTING:
                        # TODO
                        pass
                else:
                    duration = self.move(duration)
                    if duration > 0 and self.work != HumanWork.IDLE:
                        self.set_target_location(self.target_location if self.going_to_work else self.building_location)

class Colonist(Human):
    def __init__(self, map, location, player):
        super().__init__(100, HumanType.COLONIST, 100, 10, 10, map, location, player)