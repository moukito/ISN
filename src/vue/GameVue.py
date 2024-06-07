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
    __slots__ = ["saver", "player", "map", "clicked_building", "camera_pos", "left_clicking", "right_clicking", "button_hovered", "start_click_pos", "mouse_pos", "select_start", "select_end", "selecting", "selected_humans", "building", "building_pos", "screen_width", "screen_height", "screen_size", "ressource_background_size", "building_button", "home_button", "building_button_rect", "home_button_rect", "clock", "last_timestamp", "building_choice", "building_choice_displayed", "building_interface", "building_interface_displayed"]

    def __init__(self, core):
        super().__init__(core)

        self.ressource_background_size = None
        self.clicked_building = None
        self.home_button = None
        self.building_button = None
        self.home_button_rect = None
        self.building_button_rect = None
        self.building_pos = None
        self.building = None

        self.player = Player(self.ressource_update_callback)

        self.map = Map()

        self.left_clicking = False
        self.right_clicking = False
        self.button_hovered = False
        self.camera_pos = Point.origin()
        self.start_click_pos = Point.origin()
        self.mouse_pos = Point.origin()

        self.select_start = Point.origin()
        self.select_end = Point.origin()
        self.selecting = False
        self.selected_humans = []

        self.reset_building()

        self.screen_width, self.screen_height = self.screen.get_width(), self.screen.get_height()
        self.screen_size = Point(self.screen_width, self.screen_height)

        self.building_choice = BuildingChoice(self.player, self.screen, self.screen_size, self.ressource_background_size, self.ressource_icons)
        self.building_choice_displayed = False

        self.building_interface = BuildingInterface(self.player, self.screen, self.screen_size, self.ressource_background_size, self.ressource_icons)
        self.building_interface_displayed = False

        self.initialize_camps()

        self.clock = pygame.time.Clock()

        self.saver = Saver(self, core.save_name)

        # TODO
        if core.save_name is not None:
            self.saver.load()

        self.last_timestamp = time_ns()

    def reset_building(self):
        self.building = None
        self.building_pos = Point.origin()

    def handle_events(self, event):
        mouse_pos = pygame.mouse.get_pos()
        mouse_point = Point(mouse_pos[0], mouse_pos[1])
        home_button_hovered, building_button_hovered = self.home_button_rect.containsPoint(mouse_point), self.building_button_rect.containsPoint(mouse_point)

        # Events for the building choice interface 
        if self.building_choice_displayed and self.building_choice.rect.containsPoint(mouse_point):
            result = self.building_choice.event_stream(event)
            if result is not None:
                self.building = get_struct_class_from_type(result)(self.camera_pos // Map.CELL_SIZE, self.player, self.building_destroyed_callback, self.human_died_callback)
                self.building_pos = mouse_point - self.screen_size // 2
                self.building_choice_displayed = False
        # Events for the building interface
        elif self.building_interface_displayed and self.building_interface.rect.containsPoint(mouse_point):
            if self.building_interface.event_stream(event):
                buttons = self.clicked_building.get_buttons(self)
                if len(buttons) > 0:
                    self.building_interface.create_buttons(buttons)
        # Events for the buttons
        elif home_button_hovered or building_button_hovered:
            self.button_hovered = True
            clicked_button = self.home_button if home_button_hovered else self.building_button
            clicked = clicked_button.is_clicked(event)
            if clicked:
                clicked_button.color = (115, 207, 255)
                if home_button_hovered:
                    self.camera_pos = Point.origin()
                else:
                    self.building_choice_displayed = not self.building_choice_displayed
            if clicked_button.is_hovered(event):
                clicked_button.color = (101, 195, 255)
            elif not clicked:
                clicked_button.color = (46, 159, 228)
        else: # Events for the game
            # MOUSE BUTTON DOWN
            if event.type == pygame.MOUSEBUTTONDOWN:
                pressed_mouse_buttons = pygame.mouse.get_pressed()
                if pressed_mouse_buttons[0]:
                    self.left_clicking = True
                    self.select_start = mouse_point
                    self.select_end = self.select_start
                elif pressed_mouse_buttons[2]:
                    self.right_clicking = True
                    if self.building is None:
                        self.mouse_pos = mouse_point
                self.start_click_pos = mouse_point
            # MOUSE BUTTON UP
            elif event.type == pygame.MOUSEBUTTONUP:
                pressed_mouse_buttons = pygame.mouse.get_pressed()

                if not pressed_mouse_buttons[2] and self.right_clicking:
                    self.right_clicking = False
                elif not pressed_mouse_buttons[0]:
                    if self.building is not None:
                        self.building.coords = self.building_pos // Map.CELL_SIZE + self.camera_pos // Map.CELL_SIZE
                        if self.left_clicking and self.map.place_structure(self.building):
                            for ressource_type, ressource_number in self.building.costs.items():
                                self.player.add_ressource(ressource_type, -ressource_number)
                            self.reset_building()
                            self.left_clicking = False
                    elif self.selecting:
                        self.selecting = False
                        self.left_clicking = False
                        self.select_start = Point.origin()
                        self.select_end = Point.origin()
                    elif len(self.selected_humans) > 0:
                        self.left_clicking = False
                        cell = (mouse_point + self.camera_pos - self.screen_size // 2) // Map.CELL_SIZE
                        for human in self.selected_humans:
                            human.set_target_location(cell)
                        self.selected_humans.clear()
                    else:
                        pos_point = mouse_point + self.camera_pos - self.screen_size // 2
                        cell_pos = pos_point // Map.CELL_SIZE
                        chunk_pos = cell_pos // Perlin.CHUNK_SIZE
                        chunk_humans = self.map.chunk_humans.get(chunk_pos, None)
                        if chunk_humans is not None:
                            for human in chunk_humans:
                                if Circle(human.current_location, 15).contains(pos_point + self.camera_pos):
                                    self.selected_humans.append(human)
                                    self.selecting = False
                                    break

                        building = self.map.occupied_coords.get(cell_pos, None)
                        if building is not None and building.structure_type == StructureType.BUILDING and building.state == BuildingState.BUILT:
                            if self.building_interface_displayed:
                                self.clicked_building = None
                                self.building_interface_displayed = False
                            else:
                                buttons = building.get_buttons(self)
                                if len(buttons) > 0:
                                    self.clicked_building = building
                                    self.building_interface_displayed = True
                                    self.building_interface.create_buttons(buttons)
                        else:
                            if self.building_interface_displayed and self.left_clicking:
                                self.building_interface_displayed = False
                            
                        self.left_clicking = False
            # MOUSE MOTION
            elif event.type == pygame.MOUSEMOTION:
                if self.button_hovered:
                    self.button_hovered = False
                    self.building_button.color = (46, 159, 228)
                    self.home_button.color = (46, 159, 228)

                if self.selecting:
                    self.select_end = mouse_point
                elif self.right_clicking:
                    self.camera_pos += (self.mouse_pos - mouse_point) * (2.8 / 2.0)
                elif self.building is not None:
                    if (self.mouse_pos - self.building_pos) // Map.CELL_SIZE != Point.origin():
                        self.building_pos = mouse_point - self.screen_size // 2
                elif self.left_clicking and self.start_click_pos.distance(mouse_point) > 10:
                    self.selecting = True
                self.mouse_pos = mouse_point
            # KEY UP
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_p :
                    pause = Pause(
                        self.core, self.render
                    )  # Create and run the settings scene
                    pause.run()
                if event.key == pygame.K_s: # TODO: temporary
                    self.saver.save()
                if event.key == pygame.K_h: # TODO: For debug, remove for the final version
                    chunk_pos = self.camera_pos // Map.CELL_SIZE // Perlin.CHUNK_SIZE
                    if self.map.chunk_humans.get(chunk_pos, None) is None:
                        self.map.chunk_humans[chunk_pos] = []
                    human = Colon(self.map, self.camera_pos, self.player, self.human_died_callback)
                    self.map.chunk_humans[chunk_pos].append(human)
                    self.map.humans.append(human)
                if event.key == pygame.K_r: # TODO: For debug, remove for the final version
                    self.player.add_ressource(RessourceType.WOOD, 1000)
                    self.player.add_ressource(RessourceType.FOOD, 1000)
                    self.player.add_ressource(RessourceType.STONE, 1000)
                    self.player.add_ressource(RessourceType.IRON, 1000)
                    self.player.add_ressource(RessourceType.COPPER, 1000)
                    self.player.add_ressource(RessourceType.GOLD, 1000)
                    self.player.add_ressource(RessourceType.CRYSTAL, 1000)
                    self.player.add_ressource(RessourceType.VULCAN, 1000)
                if event.key == pygame.K_ESCAPE:
                    self.reset_building()
                    self.selected_humans.clear()

    def update(self):
        timestamp = time_ns()
        duration = (timestamp - self.last_timestamp) / 1000000000
        self.last_timestamp = timestamp

        self.map.update(duration)

    def render(self):
        pass

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