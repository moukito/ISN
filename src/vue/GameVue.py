from math import ceil
from time import time, time_ns

import pygame

from vue.Scene import Scene

from model.Tools import Colors
from model.Map import Map, Biomes
from model.Geometry import Point, Rectangle, Circle
from model.Perlin import Perlin
from model.Player import Player
from model.Ressource import RessourceType
from model.Structures import StructureType, BaseCamp, Farm
from model.Human import Colonist
from model.Saver import Saver


class GameVue(Scene):
    __slots__ = [
        "saver",
        "player",
        "map",
        "actual_chunks",
        "buildings",
        "camera_pos",
        "frame_render",
        "clicking",
        "moving",
        "camera_moved",
        "start_click_pos",
        "mouse_pos",
        "select_start",
        "select_end",
        "selecting",
        "selected_humans",
        "building_moved",
        "building",
        "building_pos",
        "building_pos_old",
        "screen_width",
        "screen_height",
        "screen_size",
        "cell_width_count",
        "cell_height_count",
        "ressource_font",
        "ressource_icons",
        "ressource_background",
        "ressource_background_size",
        "biomes_textures",
        "colors",
        "clock",
        "last_timestamp",
    ]

    def __init__(self, core):
        super().__init__(core)

        self.colors = None
        self.ressource_background_size = None
        self.ressource_background = None
        self.biomes_textures = None
        self.ressource_icons = None
        self.ressource_font = None
        self.building_pos_old = None
        self.building_pos = None
        self.building = None
        self.building_moved = None

        self.saver = Saver()

        self.player = Player(self.ressource_update_callback)

        self.map = Map()
        self.actual_chunks = None
        self.buildings = []

        self.frame_render = False
        self.clicking = False
        self.moving = False
        self.camera_moved = True
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
        self.cell_width_count = ceil(self.screen_size.x / Map.CELL_SIZE)
        self.cell_height_count = ceil(self.screen_height / Map.CELL_SIZE)

        self.load_ressources()

        self.map.place_structure(BaseCamp(Point.origin(), self.player)) # TODO : do that in a cleaner way / Do we keep the orientation as RANDOM?

        # TODO : temporary
        self.camera_pos = Point(-80, -80)
        chunk_pos = self.camera_pos // Map.CELL_SIZE // Perlin.CHUNK_SIZE
        if self.map.chunk_humans.get(chunk_pos, None) is None:
            self.map.chunk_humans[chunk_pos] = []
        human = Colonist(self.map, self.camera_pos, self.player)
        self.map.chunk_humans[chunk_pos].append(human)
        self.map.humans.append(human)
        self.frame_render = True

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
            self.ressource_icons[ressource_type] = pygame.transform.scale(
                pygame.image.load(
                    "assets/icons/" + ressource_type.name.lower() + ".png"
                ).convert_alpha(),
                (26, 26),
            )

        self.biomes_textures = {}
        for biome in Biomes:
            self.biomes_textures[biome] = pygame.transform.scale(
                pygame.image.load(
                    "assets/icons/" + biome.name.lower() + ".jpg"
                ).convert_alpha(),
                (Map.CELL_SIZE, Map.CELL_SIZE),
            )

        self.ressource_background = pygame.transform.scale(
            pygame.image.load("assets/ui.png").convert_alpha(), (312, 202)
        )
        self.ressource_background_size = (
            self.ressource_background.get_width(),
            self.ressource_background.get_height(),
        )

        self.colors = {
            Colors.BLACK: pygame.Color(pygame.color.THECOLORS["black"]),
            Colors.WHITE: pygame.Color(pygame.color.THECOLORS["white"]),
            Colors.ALICEBLUE: pygame.Color(pygame.color.THECOLORS["aliceblue"]),
            Colors.AQUA: pygame.Color(pygame.color.THECOLORS["aqua"]),
            Colors.BLUE: pygame.Color(pygame.color.THECOLORS["blue"]),
            Colors.BLUEVIOLET: pygame.Color(pygame.color.THECOLORS["blueviolet"]),
            Colors.RED: pygame.Color(pygame.color.THECOLORS["red"]),
            Colors.ORANGE: pygame.Color(pygame.color.THECOLORS["orange"]),
            Colors.YELLOW: pygame.Color(pygame.color.THECOLORS["yellow"]),
        }

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pressed_mouse_buttons = pygame.mouse.get_pressed()
            if pressed_mouse_buttons[2]:
                self.selecting = True
                self.selected_humans.clear()
                pos = pygame.mouse.get_pos()
                self.select_start = Point(pos[0], pos[1])
                self.select_end = self.select_start
            elif pressed_mouse_buttons[0]:
                if self.building is None:
                    self.clicking = True
                    pos = pygame.mouse.get_pos()
                    self.mouse_pos = self.start_click_pos = Point(pos[0], pos[1])
        elif event.type == pygame.MOUSEBUTTONUP:
            pressed_mouse_buttons = pygame.mouse.get_pressed()
            if not pressed_mouse_buttons[0] and self.clicking:
                if len(self.selected_humans) > 0:
                    pos = pygame.mouse.get_pos()
                    pos_point = Point(pos[0], pos[1])
                    cell = (pos_point + self.camera_pos - self.screen_size // 2) // Map.CELL_SIZE
                    for human in self.selected_humans:
                        human.set_target_location(cell)
                    self.selected_humans.clear()
                    self.frame_render = True
                if self.building is not None or self.clicking:
                    if self.building is None:
                        if not self.moving:
                            pos = pygame.mouse.get_pos()
                            pos_point = Point(pos[0], pos[1]) + self.camera_pos - self.screen_size // 2
                            chunk_pos = pos_point // Map.CELL_SIZE // Perlin.CHUNK_SIZE
                            if self.map.chunk_humans.get(chunk_pos, None) is not None:
                                for human in self.map.chunk_humans[chunk_pos]:
                                    if Circle(human.current_location, 10).contains(pos_point):
                                        self.selected_humans.append(human)
                                        self.selecting = False
                                        break
                                self.frame_render = len(self.selected_humans) > 0
                        self.clicking = False
                        self.moving = False
                    else:
                        self.building.coords = (
                                                    self.building_pos
                                                    + Point(int(self.camera_pos.x), int(self.camera_pos.y))
                                                    - self.screen_size // 2
                                            ) // Map.CELL_SIZE
                        result = self.map.place_structure(self.building)
                        if result:
                            self.reset_building()
            elif not pressed_mouse_buttons[2] and self.selecting:
                self.frame_render = True
                self.selecting = False
                self.select_start = Point.origin()
                self.select_end = Point.origin()

        elif event.type == pygame.MOUSEMOTION:
            pos = pygame.mouse.get_pos()
            pos_point = Point(pos[0], pos[1])
            if self.selecting:
                self.select_end = pos_point
            elif self.clicking:
                pos = pygame.mouse.get_pos()
                pos_point = Point(pos[0], pos[1])
                # TODO: fine-tune this
                if not self.moving and self.start_click_pos.distance(pos_point) > 10:
                    self.moving = True 
                elif self.moving:
                    self.camera_pos += (self.mouse_pos - pos_point) * (2 / 2.0)
                    self.camera_moved = (self.mouse_pos - pos_point) != Point.origin()
            elif self.building is not None:
                self.building_moved = (
                                              self.mouse_pos - self.building_pos
                                      ) // Map.CELL_SIZE != Point.origin()
                if self.building_moved:
                    self.building_pos = pos_point
            self.mouse_pos = pos_point
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_p:
                if self.building is None:
                    self.building_moved = True
                    self.building = Farm(
                        Point(int(self.camera_pos.x), int(self.camera_pos.y))
                        // Map.CELL_SIZE,
                        self.player,
                    )
                    self.building_pos_old = self.building_pos
                    self.building_pos = self.mouse_pos
                else:
                    self.reset_building()
                    self.building_moved = True
            if event.key == pygame.K_s:
                self.saver.save_map(self.map)
            if event.key == pygame.K_h: # TODO : temporary
                chunk_pos = self.camera_pos // Map.CELL_SIZE // Perlin.CHUNK_SIZE
                if self.map.chunk_humans.get(chunk_pos, None) is None:
                    self.map.chunk_humans[chunk_pos] = []
                human = Colonist(self.map, self.camera_pos, self.player)
                self.map.chunk_humans[chunk_pos].append(human)
                self.map.humans.append(human)
                self.frame_render = True
            elif event.key == pygame.K_ESCAPE:
                self.running = False

    def update(self):
        timestamp = time_ns()
        duration = (timestamp - self.last_timestamp) / 1000000000
        self.last_timestamp = timestamp

        if self.map.update(duration):
            self.frame_render = True

    def render(self):
        if self.camera_moved or self.building_moved or self.selecting or self.frame_render:
            if self.frame_render:
                self.frame_render = False
            self.render_map()

            if self.camera_moved:
                self.camera_moved = False
            elif self.building_moved:
                # TODO: maybe optimize by removing the render of the entire map?
                self.building_moved = False

            self.render_selection()
            self.render_interface()

        # print(self.clock.get_fps())

        # self.clock.tick()

    def render_map(self):
        camera_pos = Point(int(self.camera_pos.x), int(self.camera_pos.y))
        camera_cell = camera_pos // Map.CELL_SIZE
        camera_offset = camera_pos % Map.CELL_SIZE
        camera_chunk = camera_cell // Perlin.CHUNK_SIZE
        camera_chunk_cell = camera_cell % Perlin.CHUNK_SIZE

        screen_center = self.screen_size // 2
        chunk_tl = screen_center - camera_chunk_cell * Map.CELL_SIZE
        chunk_br = (
                chunk_tl
                + Point(
            Perlin.CHUNK_SIZE * Map.CELL_SIZE,
            Perlin.CHUNK_SIZE * Map.CELL_SIZE,
        )
                - camera_offset
        )

        margin_tl = Point(max(0, chunk_tl.x), max(0, chunk_tl.y))
        margin_br = Point(
            max(0, self.screen_width - chunk_br.x),
            max(0, self.screen_height - chunk_br.y),
        )
        cells_tl = Point(
            ceil(margin_tl.x / Map.CELL_SIZE),
            ceil(margin_tl.y / Map.CELL_SIZE),
        )
        cells_br = Point(
            ceil(margin_br.x / Map.CELL_SIZE),
            ceil(margin_br.y / Map.CELL_SIZE),
        )
        chunks_tl = Point(
            ceil(cells_tl.x / Perlin.CHUNK_SIZE), ceil(cells_tl.y / Perlin.CHUNK_SIZE)
        )
        chunks_br = Point(
            ceil(cells_br.x / Perlin.CHUNK_SIZE), ceil(cells_br.y / Perlin.CHUNK_SIZE)
        )

        cells_tl_signed = Point(
            chunk_tl.x / Map.CELL_SIZE, chunk_tl.y / Map.CELL_SIZE
        )
        cells_br_signed = Point(
            (self.screen_width - chunk_br.x) / Map.CELL_SIZE,
            (self.screen_height - chunk_br.y) / Map.CELL_SIZE,
        )
        cells_size = Point(
            ceil(cells_tl_signed.x + cells_br_signed.x) + Perlin.CHUNK_SIZE,
            ceil(cells_tl_signed.y + cells_br_signed.y) + Perlin.CHUNK_SIZE,
        )
        chunks_size = chunks_br + chunks_tl

        ceiled_cells_tl = Point(ceil(cells_tl_signed.x), ceil(cells_tl_signed.y))
        cell_offset = Point(
            (
                -ceiled_cells_tl.x
                if ceiled_cells_tl.x <= 0
                else Perlin.CHUNK_SIZE - ceiled_cells_tl.x
            ),
            (
                -ceiled_cells_tl.y
                if ceiled_cells_tl.y <= 0
                else Perlin.CHUNK_SIZE - ceiled_cells_tl.y
            ),
        )

        tl_chunk = camera_chunk - chunks_tl
        chunks = self.map.get_area_around_chunk(
            camera_chunk - chunks_tl, chunks_size.x + 1, chunks_size.y + 1
        )
        self.actual_chunks = chunks

        # RENDER MAP
        for i in range(0, cells_size.x):
            for j in range(0, cells_size.y):
                x = i + cell_offset.x
                y = j + cell_offset.y
                self.screen.blit(
                    self.biomes_textures[Biomes(int(chunks[x][y]))],
                    (
                        i * Map.CELL_SIZE - camera_offset.x,
                        j * Map.CELL_SIZE - camera_offset.y,
                    ),
                )

        # RENDER PLACE BUILDING
        if self.building is not None:
            if self.building_pos_old != Point(-1, -1):
                # TODO: for optimization
                pass

            relative_center = self.building_pos // Map.CELL_SIZE
            for point in self.building.points:
                absolute_point = (
                                         relative_center + point
                                 ) * Map.CELL_SIZE - camera_offset
                pygame.draw.rect(
                    self.screen,
                    self.colors[
                        (
                            Colors.BLACK
                            if self.map.occupied_coords.get(
                                point + self.building.coords, None
                            )
                               is None
                            else Colors.RED
                        )
                    ],
                    (
                        absolute_point.x,
                        absolute_point.y,
                        Map.CELL_SIZE,
                        Map.CELL_SIZE,
                    ),
                )


        if self.selecting:
            self.selected_humans.clear()
            selection_rect = Rectangle.fromPoints(self.select_start, self.select_end)
        else:
            ids = [id(h) for h in self.selected_humans]

        # RENDER STRUCTURES AND HUMANS
        # TODO : fix the offset
        for x in range(tl_chunk.x, tl_chunk.x + chunks_size.x + 1):
            for y in range(tl_chunk.y, tl_chunk.y + chunks_size.y + 1):
                actual_chunk_occupied_coords = self.map.chunk_occupied_coords.get(
                    Point(x, y), None
                )
                if actual_chunk_occupied_coords is not None:
                    for point in actual_chunk_occupied_coords:
                        struct = self.map.occupied_coords.get(point, None)
                        if (
                                struct is not None
                        ):
                            absolute_point = (
                                    (point - camera_cell) * Map.CELL_SIZE
                                    + screen_center
                                    - camera_offset
                            )
                            pygame.draw.rect(
                                self.screen,
                                self.colors[Colors.BLACK if struct.structure_type == StructureType.BUILDING else Colors.BLUE],
                                (
                                    absolute_point.x,
                                    absolute_point.y,
                                    Map.CELL_SIZE,
                                    Map.CELL_SIZE,
                                ),
                            )
                
                actual_chunk_humans = self.map.chunk_humans.get(Point(x, y), None)
                if actual_chunk_humans is not None:
                    for human in actual_chunk_humans:
                        absolute_point = (
                                human.current_location
                                - camera_cell * Map.CELL_SIZE
                                + screen_center
                                - camera_offset
                        )

                        if self.selecting:
                            selected = selection_rect.containsPoint(absolute_point)
                            if selected:
                                self.selected_humans.append(human)
                        else:
                            selected = id(human) in ids

                        pygame.draw.circle(
                            self.screen,
                            self.colors[Colors.BLUE if selected else Colors.AQUA],
                            (absolute_point.x, absolute_point.y),
                            10,
                        )
                

    def render_selection(self):
        if self.selecting:
            s = pygame.Surface((abs(self.select_end.x - self.select_start.x), abs(self.select_end.y - self.select_start.y)))
            s.set_alpha(150)
            s.fill((0,127,127))
            self.screen.blit(s, (self.select_start.x if self.select_start.x < self.select_end.x else self.select_end.x, self.select_start.y if self.select_start.y < self.select_end.y else self.select_end.y))

    def render_interface(self):
        # TODO : store the map under the interface in a buffer to refresh only the interface when needed and not the entire map
        ressource_icons_texts = {}
        for ressource_type in RessourceType:
            text = self.render_ressource_text(ressource_type)
            icon = self.ressource_icons.get(ressource_type, None)
            ressource_icons_texts[ressource_type] = (icon, text)

        offset = self.screen_height - self.ressource_background_size[1]

        self.screen.blit(self.ressource_background, (0, offset))

        i = 0
        for ressource_type in [
            (RessourceType.FOOD, RessourceType.COPPER),
            (RessourceType.WOOD, RessourceType.IRON),
            (RessourceType.STONE, RessourceType.CRYSTAL),
            (RessourceType.GOLD, RessourceType.VULCAN),
        ]:
            ressource_1, ressource_2 = ressource_type

            ressource_icon_1, ressource_text_1 = ressource_icons_texts.get(
                ressource_1, (None, None)
            )
            ressource_icon_2, ressource_text_2 = ressource_icons_texts.get(
                ressource_2, (None, None)
            )

            self.screen.blit(ressource_text_1, (80, offset + 50 + 30 * i))
            self.screen.blit(ressource_text_2, (200, offset + 50 + 30 * i))

            self.screen.blit(ressource_icon_1, (40, offset + 43 + 30 * i))
            self.screen.blit(ressource_icon_2, (160, offset + 43 + 30 * i))

            i += 1

    def render_ressource_text(self, ressource_type):
        return self.ressource_font.render(
            str(int(self.player.get_ressource(ressource_type))),
            True,
            self.colors[Colors.WHITE],
        )
    
    def ressource_update_callback(self):
        self.frame_render = True