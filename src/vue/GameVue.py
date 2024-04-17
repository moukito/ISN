import pygame

from Scene import Scene

from model.Map import Map
from model.Geometry import Point
from model.Perlin import Perlin


class GameVue(Scene):
    __slots__ = ["map", "camera_pos", "camera_moved", "clicking", "start_click_pos", "mouse_pos"]

    def __init__(self):
        super().__init__()
        self.map = Map()
        self.clicking = False
        self.camera_moved = True
        self.start_click_pos = Point.origin()
        self.mouse_pos = Point.origin()
        self.camera_pos = Point.origin()

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pressed_mouse_buttons = pygame.mouse.get_pressed()
            if pressed_mouse_buttons[0]:
                self.clicking = True
                self.mouse_pos = self.start_click_pos = pygame.mouse.get_pos()
        elif event.type == pygame.MOUSEBUTTONUP:
            pressed_mouse_buttons = pygame.mouse.get_pressed()
            if not pressed_mouse_buttons[0]:
                self.clicking = False
        elif event.type == pygame.MOUSEMOTION:
            pos  = pygame.mouse.get_pos()
            self.camera_pos += (self.mouse_pos - pos) * 2
            self.mouse_pos = pos
            self.camera_moved = True

    def update(self):
        pass

    def render(self):
        if self.camera_moved:
            colors = [pygame.Color(pygame.color.THECOLORS["aliceblue"]), pygame.Color(pygame.color.THECOLORS["aqua"]), pygame.Color(pygame.color.THECOLORS["blue"]), pygame.Color(pygame.color.THECOLORS["blueviolet"]), pygame.Color(pygame.color.THECOLORS["red"]), pygame.Color(pygame.color.THECOLORS["black"])]
            chunks = self.map.get_area_around_chunk(self.camera_pos // Perlin.CHUNK_SIZE)
            
            cell_pixel_size = 5
            width, height = self.screen.get_desktop_sizes()[0][0], self.screen.get_desktop_sizes()[0][1]
            cell_width_count = width // cell_pixel_size + (1 if width % cell_pixel_size else 0)
            cell_height_count = height // cell_pixel_size + (1 if height % cell_pixel_size else 0)
            x_start_index = (chunks.shape[0] - cell_width_count) // 2
            y_start_index = (chunks.shape[1] - cell_height_count) // 2

            for i in range(x_start_index, chunks.shape[0] - x_start_index):
                for j in range(y_start_index, chunks.shape[1] - y_start_index):
                    display = pygame.display
                    pygame.draw.rect(display, chunks[i][j], (i * cell_pixel_size, j * cell_pixel_size, cell_pixel_size, cell_pixel_size))

            self.camera_moved = False
