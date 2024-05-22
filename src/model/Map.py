from enum import Enum
import random

import matplotlib.pyplot as plt
import numpy as np

from model.Perlin import Perlin
from model.Structures import StructureType, Ore, OreType 
from model.Geometry import Point


class Biomes(Enum):
    LAVA = 1
    VOLCANO = 2
    PLAIN = 3
    MUSHROOM_FOREST = 4
    DESOLATED_FOREST = 5
    SNOW = 6

class Map:
    __slots__ = ["perlin", "map_chunks", "ores", "buildings", "building_type", "structures", "humans", "occupied_coords", "chunk_occupied_coords"]

    CELL_SIZE = 30

    def __init__(self, seed = 1) -> None:
        self.perlin = Perlin(seed, 4, 2, 1, 50, 1)
        #self.perlin = Perlin(seed, 4, 2, 2, 100, 1)
        self.map_chunks = {}
        self.ores = {} # {Point (chunk coords): {OreType: Point}} TODO : Maybe change to {Point (chunk coords): {OreType: Ore}}
        self.buildings = []
        self.building_type = {} # {StructureType: Structure}
        self.structures = {} # {Point (chunk coords): [Structure]}
        self.humans = {} # {Point (chunk coords): [Human]}
        self.occupied_coords = {} # {Point: Structure}
        self.chunk_occupied_coords = {} # {Point (chunk coords): [Point]}

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

                ore = Ore(ore_type, position)
                absolute_chunk_origin = chunk_coords * Perlin.CHUNK_SIZE
                found = False
                i = 0
                while not found and i < len(ore.points):
                    if self.occupied_coords.get(ore.points[i] + absolute_chunk_origin, None) != None:
                        found = True
                    i += 1

                if not found:
                    # TODO: maybe remove the code below in favor of self.ores?
                    for point in ore.points:
                        self.occupied_coords[absolute_chunk_origin + position + point] = ore
                        absolute_point = position + point + absolute_chunk_origin
                        self.occupied_coords[absolute_point] = ore
                        chunk_coords = absolute_point // Perlin.CHUNK_SIZE
                        if self.chunk_occupied_coords.get(chunk_coords, None) == None:
                            self.chunk_occupied_coords[chunk_coords] = []
                        self.chunk_occupied_coords[chunk_coords].append(absolute_point)

    def process_chunk(self, chunk_data, chunk_coords):
        processed_chunk = np.empty((Perlin.CHUNK_SIZE, Perlin.CHUNK_SIZE))
        for i in range(Perlin.CHUNK_SIZE):
            for j in range(Perlin.CHUNK_SIZE):
                height = chunk_data[i][j]
                position = Point(i, j)
                # TODO : Fine tune the values
                if height > 3.5:
                    processed_chunk[i][j] = Biomes.SNOW.value
                    self.try_generate_ore(chunk_coords, position, 0.005, 3, [OreType.CRYSTAL], 3, OreType.CRYSTAL)
                elif height > 2:
                    processed_chunk[i][j] = Biomes.DESOLATED_FOREST.value
                    self.try_generate_ore(chunk_coords, position, 0.01, 1, [OreType.COPPER], 2, OreType.COPPER)
                elif height > 1:
                    processed_chunk[i][j] = Biomes.MUSHROOM_FOREST.value
                elif height > -2:
                    processed_chunk[i][j] = Biomes.PLAIN.value
                    self.try_generate_ore(chunk_coords, position, 0.015, 1, [OreType.IRON], 2, OreType.IRON)
                elif height > -3:
                    processed_chunk[i][j] = Biomes.VOLCANO.value
                    self.try_generate_ore(chunk_coords, position, 0.005, 5, [OreType.VULCAN], 1, OreType.VULCAN)
                else:
                    processed_chunk[i][j] = Biomes.LAVA.value
        return processed_chunk
    
    def get_chunk(self, chunk_coords):
        if self.map_chunks.get(chunk_coords, None) is None:
            chunk = self.perlin.get_chunk(chunk_coords.x, chunk_coords.y)
            processed_chunk = self.process_chunk(chunk[0], chunk_coords)
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
        while i < l and self.occupied_coords.get(center + structure.points[i], None) == None:
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
                if self.chunk_occupied_coords.get(chunk_coords, None) == None:
                    self.chunk_occupied_coords[chunk_coords] = []
                self.chunk_occupied_coords[chunk_coords].append(absolute_point)
                
            if self.structures.get(center // Perlin.CHUNK_SIZE, None) == None:
                self.structures[center // Perlin.CHUNK_SIZE] = []
            self.structures[center // Perlin.CHUNK_SIZE].append(structure)
            if structure.structure_type == StructureType.BUILDING:
                self.buildings.append(structure)
                type = structure.type
                if self.building_type.get(type, None) == None:
                    self.building_type[type] = []
                self.building_type[type].append(structure)

        return can_place
    
    def update(self, duration):
        for building in self.buildings:
           building.update(duration)