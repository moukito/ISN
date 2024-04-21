from math import ceil

import pygame

from vue.Scene import Scene

from model.Map import Map
from model.Geometry import Point
from model.Perlin import Perlin


class GameVue(Scene):
    __slots__ = ["map", "camera_pos", "camera_moved", "clicking", "start_click_pos", "mouse_pos", "cell_pixel_size", "screen_width", "screen_height", "cell_width_count", "cell_height_count"]

    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.map = Map()
        self.clicking = False
        self.camera_moved = True
        self.start_click_pos = Point.origin()
        self.mouse_pos = Point.origin()
        self.camera_pos = Point.origin()
        
        self.cell_pixel_size = 15
        self.screen_width, self.screen_height = self.screen.get_width(), self.screen.get_height()
        self.cell_width_count = ceil(self.screen_width / self.cell_pixel_size)
        self.cell_height_count = ceil(self.screen_height / self.cell_pixel_size)

    def handle_events(self, event):
        #print(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            pressed_mouse_buttons = pygame.mouse.get_pressed()
            if pressed_mouse_buttons[0]:
                self.clicking = True
                pos = pygame.mouse.get_pos()
                self.mouse_pos = self.start_click_pos = Point(pos[0], pos[1])
        elif event.type == pygame.MOUSEBUTTONUP:
            pressed_mouse_buttons = pygame.mouse.get_pressed()
            if not pressed_mouse_buttons[0]:
                self.clicking = False
        elif event.type == pygame.MOUSEMOTION:
            if self.clicking:
                pos  = pygame.mouse.get_pos()
                pos_point = Point(pos[0], pos[1])
                self.camera_pos += (self.mouse_pos - pos_point) * (2 / 2.0)
                #print(self.camera_pos)
                self.mouse_pos = pos_point
                self.camera_moved = True
                #print(self.camera_moved)

    def update(self):
        pass

    def render(self):
        if self.camera_moved:
            colors = [pygame.Color(pygame.color.THECOLORS["aliceblue"]), pygame.Color(pygame.color.THECOLORS["aqua"]), pygame.Color(pygame.color.THECOLORS["blue"]), pygame.Color(pygame.color.THECOLORS["blueviolet"]), pygame.Color(pygame.color.THECOLORS["red"]), pygame.Color(pygame.color.THECOLORS["orange"]), pygame.Color(pygame.color.THECOLORS["yellow"]), pygame.Color(pygame.color.THECOLORS["black"])]
            camera_pos = Point(int(self.camera_pos.x), int(self.camera_pos.y))
            
            offset = camera_pos % self.cell_pixel_size
            cell_pos = camera_pos // self.cell_pixel_size

            print(cell_pos // Perlin.CHUNK_SIZE, ceil(self.cell_width_count / Perlin.CHUNK_SIZE) + 1, ceil(self.cell_height_count / Perlin.CHUNK_SIZE) + 1)
            chunks = self.map.get_area_around_chunk((cell_pos) // Perlin.CHUNK_SIZE - Point(self.cell_width_count, self.cell_height_count) // Perlin.CHUNK_SIZE, ceil(self.cell_width_count / Perlin.CHUNK_SIZE) + 1, ceil(self.cell_height_count / Perlin.CHUNK_SIZE) + 1)
            
            for i in range(0, chunks.shape[0]):
                for j in range(0, chunks.shape[1]):
                    #pygame.draw.rect(self.screen, colors[int(chunks[i][j])] if (i % Perlin.CHUNK_SIZE and j % Perlin.CHUNK_SIZE) else pygame.Color(pygame.color.THECOLORS["black"]), ((i - (chunks.shape[0] - self.cell_width_count) // 2 - cell_pos.x % Perlin.CHUNK_SIZE) * self.cell_pixel_size - offset.x, (j - (chunks.shape[1] - self.cell_height_count) // 2 - cell_pos.y % Perlin.CHUNK_SIZE) * self.cell_pixel_size - offset.y, self.cell_pixel_size, self.cell_pixel_size))
                    pygame.draw.rect(self.screen, colors[int(chunks[i][j])], ((i - (chunks.shape[0] - self.cell_width_count) // 2 - cell_pos.x % Perlin.CHUNK_SIZE) * self.cell_pixel_size - offset.x, (j - (chunks.shape[1] - self.cell_height_count) // 2 - cell_pos.y % Perlin.CHUNK_SIZE) * self.cell_pixel_size - offset.y, self.cell_pixel_size, self.cell_pixel_size))

            self.camera_moved = False

            pygame.display.flip()
