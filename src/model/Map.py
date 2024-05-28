from enum import Enum
from math import inf
import random

import matplotlib.pyplot as plt
import numpy as np

from model.Perlin import Perlin
from model.Structures import StructureType, Tree, Ore, OreType
from model.Geometry import Point, Rectangle


class Biomes(Enum):
    LAVA = 1
    VOLCANO = 2
    DESERT = 3
    PLAIN = 4
    TUNDRA = 5
    MUSHROOM_FOREST = 6
    OASIS = 7
    SWAMP = 8
    FOREST = 9
    MOUNTAIN = 10
    SNOWY_PEAK = 11
    OCEAN = 12
    BEACH = 13
    ICE_FLOE = 14

class Map:
    __slots__ = ["perlin_temperature", "perlin_humidity", "map_chunks", "trees", "ores", "buildings", "building_type", "structures", "occupied_coords", "chunk_humans", "humans", "chunk_occupied_coords", "temp_humi_biomes"]

    CELL_SIZE = 30

    def __init__(self, seed = 1) -> None:
        self.perlin_temperature = Perlin(seed, 4, 2, 1, 50, 1)
        self.perlin_humidity = Perlin(seed + 10, 4, 2, 1, 50, 1)
        #self.perlin = Perlin(seed, 4, 2, 2, 100, 1)
        self.map_chunks = {}
        self.trees = {} # {Point (chunk coords): [Point]}
        self.ores = {} # {Point (chunk coords): {OreType: [Point]}}
        self.buildings = []
        self.building_type = {} # {StructureType: Structure}
        self.structures = {} # {Point (chunk coords): [Structure]}
        self.occupied_coords = {} # {Point: Structure}
        self.chunk_humans = {} # {Point (chunk coords): [Humans]}
        self.humans = []
        self.chunk_occupied_coords = {} # {Point (chunk coords): [Point]}

        self.temp_humi_biomes = { # Rectangle(min_humi, min_temp, max_humi, max_temp): Biome
            Rectangle(-inf,  3  , -2  ,  inf): Biomes.LAVA,
            Rectangle(-inf,  2  , -2  ,  3  ): Biomes.VOLCANO,
            Rectangle(-inf,  0.5, -2  ,  2  ): Biomes.DESERT,
            Rectangle(-inf, -2.5, -2  ,  0.5): Biomes.PLAIN,
            Rectangle(-inf, -inf, -2  , -2.5): Biomes.TUNDRA,
            Rectangle(-2  ,  2.5,  3  ,  inf): Biomes.MUSHROOM_FOREST,
            Rectangle(-2  ,  1  ,  1  ,  2.5): Biomes.OASIS,
            Rectangle( 1  ,  1  ,  3  ,  2.5): Biomes.SWAMP,
            Rectangle(-2  , -1  ,  2  ,  1  ): Biomes.FOREST,
            Rectangle(-2  , -2.5,  2  , -1  ): Biomes.MOUNTAIN,
            Rectangle(-2  , -inf,  2  , -2.5): Biomes.SNOWY_PEAK,
            Rectangle( 3  , -2.5,  inf,  inf): Biomes.OCEAN,
            Rectangle( 2  , -2.5,  3  ,  1  ): Biomes.BEACH,
            Rectangle( 2  , -inf,  inf, -2.5): Biomes.ICE_FLOE
        }
    
    def try_generate_tree(self, chunk_coords, position, treshold, search_area_size, tree_count_treshold):
        if random.random() < treshold:
            trees_count = 0
            values = [0]
            for i in range(1, search_area_size // 2 + 1):
                values.append(-i)
                values.append(i)

            for i in range(search_area_size * search_area_size):
                chunk_trees = self.trees.get(Point(chunk_coords.x + values[i // search_area_size], chunk_coords.y + values[i % search_area_size]), None)
                if chunk_trees != None:
                    trees_count += len(chunk_trees)

            if trees_count < tree_count_treshold:
                if self.trees.get(chunk_coords, None) == None:
                    self.trees[chunk_coords] = []

                absolute_position = chunk_coords * Perlin.CHUNK_SIZE + position
                tree = Tree(absolute_position, self.tree_chopped_callback)
                found = False
                i = 0
                while not found and i < len(tree.points):
                    if self.occupied_coords.get(tree.points[i] + absolute_position, None) is not None:
                        found = True
                    i += 1

                if not found:
                    self.trees[chunk_coords].append(absolute_position)
                    for point in tree.points:
                        self.occupied_coords[absolute_position + point] = tree
                        chunk_pos = (absolute_position + point) // Perlin.CHUNK_SIZE
                        if self.chunk_occupied_coords.get(chunk_pos, None) is None:
                            self.chunk_occupied_coords[chunk_pos] = []
                        self.chunk_occupied_coords[chunk_pos].append(absolute_position + point)

    def try_generate_ore(self, chunk_coords, position, treshold, search_area_size, search_ores, ores_count_treshold, ore_type):
        if random.random() < treshold:
            ores_count = 0
            values = [0]
            for i in range(1, search_area_size // 2 + 1):
                values.append(-i)
                values.append(i)
                
            for i in range(search_area_size * search_area_size):
                chunk_ores = self.ores.get(Point(chunk_coords.x + values[i // search_area_size], chunk_coords.y + values[i % search_area_size]), None)
                if chunk_ores != None:
                    for search_ore in search_ores:
                        actual_chunk_ores = chunk_ores.get(search_ore, None)
                        if actual_chunk_ores != None:
                            ores_count += len(actual_chunk_ores)

            if ores_count < ores_count_treshold:
                if self.ores.get(chunk_coords, None) == None:
                    self.ores[chunk_coords] = {}
                if self.ores[chunk_coords].get(ore_type, None) == None:
                    self.ores[chunk_coords][ore_type] = []

                absolute_position = chunk_coords * Perlin.CHUNK_SIZE + position
                ore = Ore(ore_type, absolute_position, self.ore_mined_callback)
                found = False
                i = 0
                while not found and i < len(ore.points):
                    if self.occupied_coords.get(ore.points[i] + absolute_position, None) is not None:
                        found = True
                    i += 1

                if not found:
                    self.ores[chunk_coords][ore_type].append(absolute_position)
                    for point in ore.points:
                        self.occupied_coords[absolute_position + point] = ore
                        chunk_pos = (absolute_position + point) // Perlin.CHUNK_SIZE
                        if self.chunk_occupied_coords.get(chunk_pos, None) is None:
                            self.chunk_occupied_coords[chunk_pos] = []
                        self.chunk_occupied_coords[chunk_pos].append(absolute_position + point)


    def process_chunk(self, chunk_temperature_data, chunk_humidity_data, chunk_coords):
        processed_chunk = np.empty((Perlin.CHUNK_SIZE, Perlin.CHUNK_SIZE), dtype=int)
        for i in range(Perlin.CHUNK_SIZE):
            for j in range(Perlin.CHUNK_SIZE):
                """
                humi_temp = Point(chunk_humidity_data[i][j], chunk_temperature_data[i][j])
                position = Point(i, j)

                for rect, biome in self.temp_humi_biomes.items():
                    if rect.containsPoint(humi_temp):
                        processed_chunk[i][j] = biome.value
                        break"""

                position = Point(i, j)
                height = chunk_temperature_data[i][j]
                # Do not put a treshold over 0.015, it will generate structures only at the start of the chunk
                if height > 4.5:
                    processed_chunk[i][j] = Biomes.SNOWY_PEAK.value
                    self.try_generate_ore(chunk_coords, position, 0.005, 3, [OreType.CRYSTAL], 3, OreType.CRYSTAL)
                elif height > 2.5:
                    processed_chunk[i][j] = Biomes.MOUNTAIN.value
                    self.try_generate_ore(chunk_coords, position, 0.01, 1, [OreType.COPPER], 2, OreType.COPPER)
                elif height > 0:
                    processed_chunk[i][j] = Biomes.FOREST.value
                    self.try_generate_ore(chunk_coords, position, 0.015, 1, [OreType.IRON, OreType.STONE], 2, OreType.IRON)
                    self.try_generate_tree(chunk_coords, position, 0.015, 1, 15)
                elif height > -2.75:
                    processed_chunk[i][j] = Biomes.PLAIN.value
                    self.try_generate_ore(chunk_coords, position, 0.015, 1, [OreType.STONE], 2, OreType.STONE)
                    self.try_generate_tree(chunk_coords, position, 0.01, 2, 5)
                elif height > -4:
                    processed_chunk[i][j] = Biomes.VOLCANO.value
                    self.try_generate_ore(chunk_coords, position, 0.005, 5, [OreType.VULCAN], 1, OreType.VULCAN)
                else:
                    processed_chunk[i][j] = Biomes.LAVA.value
        return processed_chunk

    def get_chunk(self, chunk_coords):
        if self.map_chunks.get(chunk_coords, None) is None:
            chunk_temperature = self.perlin_temperature.get_chunk(chunk_coords.x, chunk_coords.y)
            #chunk_humidity = self.perlin_humidity.get_chunk(chunk_coords.x, chunk_coords.y)
            processed_chunk = self.process_chunk(chunk_temperature[0], None, chunk_coords)#chunk_humidity[0], chunk_coords)
            self.map_chunks[chunk_coords] = processed_chunk
        return self.map_chunks[chunk_coords]

    def get_area_around_chunk(self, chunk_coords, width, height):
        # Get an area of <area_size> x <area_size> chunks around the current chunk, concatenated into one 2D array
        rows = []
        chunks = []
        for i in range(width):
            for j in range(height):
                actual_chunk_coords = Point(chunk_coords.x + i, chunk_coords.y + j)
                chunks.append(self.get_chunk(actual_chunk_coords))
            rows.append(np.concatenate(chunks, axis = 1))
            chunks.clear()

        return np.concatenate(rows, axis = 0)

    def try_place_structure(self, structure):
        center = structure.coords
        i = 0
        l = len(structure.points)
        while i < l and self.occupied_coords.get(center + structure.points[i], None) is None:
            i += 1

        return i == l

    def place_structure(self, structure):
        can_place = self.try_place_structure(structure)
        if can_place:
            center = structure.coords
            for relative_point in structure.points:
                absolute_point = center + relative_point
                self.occupied_coords[absolute_point] = structure
                chunk_coords = absolute_point // Perlin.CHUNK_SIZE
                if self.chunk_occupied_coords.get(chunk_coords, None) is None:
                    self.chunk_occupied_coords[chunk_coords] = []
                self.chunk_occupied_coords[chunk_coords].append(absolute_point)

            if self.structures.get(center // Perlin.CHUNK_SIZE, None) is None:
                self.structures[center // Perlin.CHUNK_SIZE] = []
            self.structures[center // Perlin.CHUNK_SIZE].append(structure)
            if structure.structure_type == StructureType.BUILDING:
                self.buildings.append(structure)
                type = structure.type
                if self.building_type.get(type, None) is None:
                    self.building_type[type] = []
                self.building_type[type].append(structure)

        return can_place
    
    def place_human(self, human, map_position):
        chunk_pos = map_position // Map.CELL_SIZE // Perlin.CHUNK_SIZE
        if self.chunk_humans.get(chunk_pos, None) is None:
            self.chunk_humans[chunk_pos] = []
        self.chunk_humans[chunk_pos].append(human)
        self.humans.append(human)

    def tree_chopped_callback(self, tree):
        try:
            self.trees[tree.coords // Perlin.CHUNK_SIZE].remove(tree.coords)
        except ValueError:
            pass

        for point in tree.points:
            try:
                actual_chunk_pos = (tree.coords + point) // Perlin.CHUNK_SIZE
                self.occupied_coords.pop(tree.coords + point)
                self.chunk_occupied_coords[actual_chunk_pos].remove(tree.coords + point)
            except Exception:
                pass
    
    def ore_mined_callback(self, ore):
        try:
            self.ores[ore.coords // Perlin.CHUNK_SIZE][ore.type].remove(ore.coords)
        except ValueError:
            pass

        for point in ore.points:
            try:
                actual_chunk_pos = (ore.coords + point) // Perlin.CHUNK_SIZE
                self.occupied_coords.pop(ore.coords + point)
                self.chunk_occupied_coords[actual_chunk_pos].remove(ore.coords + point)
            except Exception:
                pass

    def update(self, duration):
        need_render = False

        for building in self.buildings:
            building.update(duration)

        chunk_humans = self.chunk_humans.copy()
        for chunk_coords, humans in self.chunk_humans.items():
            for human in humans:
                if human.update(duration):
                    need_render = True
                    new_chunk_coords = human.current_location // Map.CELL_SIZE // Perlin.CHUNK_SIZE
                    if new_chunk_coords != chunk_coords:
                        if chunk_humans.get(new_chunk_coords, None) is None:
                            chunk_humans[new_chunk_coords] = []
                        chunk_humans[new_chunk_coords].append(human)
                        chunk_humans[chunk_coords].remove(human)
        self.chunk_humans = chunk_humans

        return need_render
