from math import ceil
from time import time, time_ns

import pygame

from vue.Scene import Scene
from vue.BuildingChoice import BuildingChoice
from vue.BuildingInterface import BuildingInterface
from vue.Button import Button
from vue.Pause import Pause

from model.Tools import Colors, Directions
from model.Map import Map, Biomes
from model.Geometry import Point, Rectangle, Circle
from model.Perlin import Perlin
from model.Player import Player
from model.Ressource import RessourceType
from model.Structures import StructureType, BuildingType, BuildingState, OreType, BaseCamp, Farm, get_struct_class_from_type
from model.Human import Human, Colon, get_human_class_from_type
from model.HumanType import HumanType
from model.Saver import Saver

class GameVue(Scene):
    # TODO: Add the scaling of the interface and the map
    __slots__ = ["saver", "player", "map", "selected_humans", "last_timestamp", "building_costs"]

    def __init__(self, core):
        super().__init__(core)

        self.player = Player(self.ressource_update_callback)

        self.map = Map()

        self.building_costs = {
            BuildingType.FARM: {RessourceType.WOOD: 50},
            BuildingType.PANTRY: {RessourceType.WOOD: 75, RessourceType.STONE: 25},
            BuildingType.MINER_CAMP: {RessourceType.WOOD: 75, RessourceType.STONE: 25},
            BuildingType.LUMBER_CAMP: {RessourceType.WOOD: 100, RessourceType.STONE: 25},
            BuildingType.HUNTER_CAMP: {RessourceType.WOOD: 50, RessourceType.STONE: 25, RessourceType.FOOD: 25},
            BuildingType.SOLDIER_CAMP: {RessourceType.WOOD: 50, RessourceType.STONE: 25, RessourceType.IRON: 50},
        }

        self.selected_humans = []

        self.initialize_camps()

        self.saver = Saver(self, core.save_name)

        # TODO
        if core.save_name is not None:
            self.saver.load()

        self.last_timestamp = time_ns()

    def handle_events(self, event):
        pass

    def update(self):
        timestamp = time_ns()
        duration = (timestamp - self.last_timestamp) / 1000000000
        self.last_timestamp = timestamp

        self.map.update(duration)

    def render(self):
        pass

    def ressource_update_callback(self):
        pass

    def place_building(self, building_type, position):
        building = get_struct_class_from_type(building_type)(position, self.player, self.building_destroyed_callback)
        result = True
        for ressource, cost in self.building_costs[building_type].items():
            if self.player.ressources[ressource] < cost:
                result = False
                break
        return result and self.map.place_structure(building, position)
    
    def buy_building_option(self, building, option):
        buttons = building.get_buttons(self)
        result = True
        if option in buttons.keys():
            for ressource, cost in buttons[option][0].items():
                if self.player.ressources[ressource] < cost:
                    result = False
                    break
            if result:
                buttons[option][2]()
        return result
    
    def select_humans(self, human):
        self.selected_humans.append(human)

    def deselect_humans(self):
        self.selected_humans.clear()

    def set_target_selected_humans(self, target):
        for human in self.selected_humans:
            human.set_target(target)

    def building_destroyed_callback(self, building):
        self.map.remove_building(building)

    def human_died_callback(self, human):
        self.map.remove_human(human)

    def initialize_camps(self):
        self.map.place_structure(BaseCamp(Point.origin(), self.player, self.building_destroyed_callback, self.human_died_callback))
        for point in [Point(-3, 1), Point(-3, 2), Point(-3, 3), Point(-2, 3), Point(-1, 3)]:
            postion = point * Map.CELL_SIZE + Human.CELL_CENTER
            human = Colon(self.map, postion, self.player, self.human_died_callback)
            self.map.place_human(human, postion)

    def add_human(self, human_type, position):
        human = get_human_class_from_type(human_type)(self.map, position * Map.CELL_SIZE, self.player, self.human_died_callback)
        chunk_pos = position // Perlin.CHUNK_SIZE
        if self.map.chunk_humans.get(chunk_pos, None) is None:
            self.map.chunk_humans[chunk_pos] = []
        self.map.chunk_humans[chunk_pos].append(human)
        self.map.humans.append(human)