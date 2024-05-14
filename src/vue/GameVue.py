from math import ceil
from time import time, time_ns

import pygame

from vue.Scene import Scene

from model.Tools import Colors
from model.Map import Map
from model.Geometry import Point
from model.Perlin import Perlin
from model.Player import Player
from model.Ressource import RessourceType
from model.Structures import BaseCamp, Farm


class GameVue(Scene):
    __slots__ = ["player", "map", "actual_chunks", "buildings", "camera_pos", "clicking", "camera_moved", "start_click_pos", "mouse_pos", "building_moved", "building", "building_pos", "building_pos_old", "cell_pixel_size", "screen_width", "screen_height", "cell_width_count", "cell_height_count", "ressource_font", "ressource_icons", "ressource_background", "ressource_background_size", "colors", "clock", "last_timestamp"]

    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)

        self.player = Player()

        self.map = Map()
        self.actual_chunks = None
        self.buildings = []

        self.clicking = False
        self.camera_moved = True
        self.camera_pos = Point.origin()
        self.start_click_pos = Point.origin()
        self.mouse_pos = Point.origin()

        self.reset_building()
        
        self.cell_pixel_size = 30
        self.screen_width, self.screen_height = self.screen.get_width(), self.screen.get_height()
        self.cell_width_count = ceil(self.screen_width / self.cell_pixel_size)
        self.cell_height_count = ceil(self.screen_height / self.cell_pixel_size)

        self.load_ressources()

        self.clock = pygame.time.Clock()

        self.last_timestamp = time_ns()

    def reset_building(self):
        self.building_moved = False
        self.building = None
        self.building_pos = Point.origin()
        self.building_pos_old = Point(-1, -1)

    def load_ressources(self):
        self.ressource_font = pygame.font.Font(None, 20)

        self.ressource_icons = {}
        for ressource_type in RessourceType:
            self.ressource_icons[ressource_type] = pygame.transform.scale(pygame.image.load("assets/icons/" + ressource_type.name.lower() + ".png").convert_alpha(), (26, 26))
        #print(self.ressource_icons.keys())

        self.ressource_background = pygame.transform.scale(pygame.image.load("assets/ui.png").convert_alpha(), (312, 202))
        self.ressource_background_size = (self.ressource_background.get_width(), self.ressource_background.get_height())
        #self.ressource_background = pygame.image.load("assets/ui.png").convert_alpha()

        self.colors = {
            Colors.BLACK: pygame.Color(pygame.color.THECOLORS["black"]), 
            Colors.WHITE: pygame.Color(pygame.color.THECOLORS["white"]),
            Colors.ALICEBLUE: pygame.Color(pygame.color.THECOLORS["aliceblue"]), 
            Colors.AQUA: pygame.Color(pygame.color.THECOLORS["aqua"]),
            Colors.BLUE: pygame.Color(pygame.color.THECOLORS["blue"]), 
            Colors.BLUEVIOLET: pygame.Color(pygame.color.THECOLORS["blueviolet"]),
            Colors.RED: pygame.Color(pygame.color.THECOLORS["red"]),
            Colors.ORANGE: pygame.Color(pygame.color.THECOLORS["orange"]),
            Colors.YELLOW: pygame.Color(pygame.color.THECOLORS["yellow"])
        }

    def handle_events(self, event):
        #print(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            pressed_mouse_buttons = pygame.mouse.get_pressed()
            if pressed_mouse_buttons[0]:
                if self.building == None:
                    self.clicking = True
                    pos = pygame.mouse.get_pos()
                    self.mouse_pos = self.start_click_pos = Point(pos[0], pos[1])
        elif event.type == pygame.MOUSEBUTTONUP:
            pressed_mouse_buttons = pygame.mouse.get_pressed()
            if not pressed_mouse_buttons[0]:
                if self.building == None:
                    self.clicking = False
                else:
                    result = self.map.place_structure(self.building)
                    print(result)
                    if result:
                        self.reset_building()
        elif event.type == pygame.MOUSEMOTION:
            pos  = pygame.mouse.get_pos()
            pos_point = Point(pos[0], pos[1])
            if self.clicking:
                pos  = pygame.mouse.get_pos()
                pos_point = Point(pos[0], pos[1])
                # TODO: fine-tune this
                self.camera_pos += (self.mouse_pos - pos_point) * (2 / 2.0)
                self.camera_moved = (self.mouse_pos - pos_point) != Point.origin()
            elif self.building != None:
                self.building_moved = (self.mouse_pos - self.building_pos) // self.cell_pixel_size != Point.origin()
                if self.building_moved:
                    self.building_pos = pos_point
            self.mouse_pos = pos_point
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_p:
                if self.building == None:
                    self.building_moved = True
                    self.building = Farm(Point(int(self.camera_pos.x), int(self.camera_pos.y)) // self.cell_pixel_size, self.player)
                    self.building_pos_old = self.building_pos
                    self.building_pos = self.mouse_pos
                else:
                    self.reset_building()
                    self.building_moved = True

    def update(self):
        timestamp = time_ns()
        duration = (timestamp - self.last_timestamp) / 1000000000
        self.last_timestamp = timestamp

        self.map.update(duration)

    def render(self):
        if self.camera_moved or self.building_moved:
            self.render_map()
            
            if self.camera_moved:
                self.camera_moved = False
            else:
                # TODO: maybe optimize by removing the render of the entire map?
                self.render_building()
                self.building_moved = False
            
            self.render_interface()

            pygame.display.flip()

        #print(self.clock.get_fps())
        
        #self.clock.tick()

    def render_map(self):
        camera_pos = Point(int(self.camera_pos.x), int(self.camera_pos.y))
        
        offset = camera_pos % self.cell_pixel_size
        cell_pos = camera_pos // self.cell_pixel_size

        #print(cell_pos // Perlin.CHUNK_SIZE, ceil(self.cell_width_count / Perlin.CHUNK_SIZE) + 1, ceil(self.cell_height_count / Perlin.CHUNK_SIZE) + 1)
        chunks = self.map.get_area_around_chunk((cell_pos) // Perlin.CHUNK_SIZE - Point(self.cell_width_count, self.cell_height_count) // Perlin.CHUNK_SIZE, ceil(self.cell_width_count / Perlin.CHUNK_SIZE) + 1, ceil(self.cell_height_count / Perlin.CHUNK_SIZE) + 1)
        self.actual_chunks = chunks
        
        # TODO: optimize
        colors = list(self.colors.values())
        for i in range(0, chunks.shape[0]):
            for j in range(0, chunks.shape[1]):
                #pygame.draw.rect(self.screen, colors[int(chunks[i][j])] if (i % Perlin.CHUNK_SIZE and j % Perlin.CHUNK_SIZE) else pygame.Color(pygame.color.THECOLORS["black"]), ((i - (chunks.shape[0] - self.cell_width_count) // 2 - cell_pos.x % Perlin.CHUNK_SIZE) * self.cell_pixel_size - offset.x, (j - (chunks.shape[1] - self.cell_height_count) // 2 - cell_pos.y % Perlin.CHUNK_SIZE) * self.cell_pixel_size - offset.y, self.cell_pixel_size, self.cell_pixel_size))
                pygame.draw.rect(self.screen, colors[int(chunks[i][j]) + 2], ((i - (chunks.shape[0] - self.cell_width_count) // 2 - cell_pos.x % Perlin.CHUNK_SIZE) * self.cell_pixel_size - offset.x, (j - (chunks.shape[1] - self.cell_height_count) // 2 - cell_pos.y % Perlin.CHUNK_SIZE) * self.cell_pixel_size - offset.y, self.cell_pixel_size, self.cell_pixel_size))
    
    def render_building(self):
        if self.building != None:
            if self.building_pos_old != Point(-1, -1):
                # TODO: for optimization
                pass

            relative_center = self.building_pos // self.cell_pixel_size
            for point in self.building.points:
                absolute_point = (relative_center + point) * self.cell_pixel_size
                pygame.draw.rect(self.screen, self.colors[Colors.BLACK], (absolute_point.x, absolute_point.y, self.cell_pixel_size, self.cell_pixel_size))

    def render_interface(self):
        ressource_icons_texts = {}
        for ressource_type in RessourceType:
            text = self.render_ressource_text(ressource_type)
            icon = self.ressource_icons.get(ressource_type, None)
            ressource_icons_texts[ressource_type] = (icon, text)

        offset = self.screen_height - self.ressource_background_size[1]

        self.screen.blit(self.ressource_background, (0, offset))

        i = 0
        for ressource_type in [(RessourceType.FOOD, RessourceType.COPPER), (RessourceType.WOOD, RessourceType.IRON), (RessourceType.STONE, RessourceType.CRYSTAL), (RessourceType.GOLD, RessourceType.VULCAN)]:
            ressource_1, ressource_2 = ressource_type

            ressource_icon_1, ressource_text_1 = ressource_icons_texts.get(ressource_1, (None, None))
            ressource_icon_2, ressource_text_2 = ressource_icons_texts.get(ressource_2, (None, None))
            
            self.screen.blit(ressource_text_1, (80 , offset + 50 + 30 * i))
            self.screen.blit(ressource_text_2, (200, offset + 50 + 30 * i))
            
            self.screen.blit(ressource_icon_1, (40 , offset + 43 + 30 * i))
            self.screen.blit(ressource_icon_2, (160, offset + 43 + 30 * i))
            
            i += 1

    def render_ressource_text(self, ressource_type):
        return self.ressource_font.render(str(self.player.get_ressource(ressource_type)), True, self.colors[Colors.WHITE])