import struct
import os
from datetime import datetime

from model.Perlin import Perlin
from model.Map import Map
from model.Structures import Structure, OreType, Building
from model.Geometry import Point

class Saver:
    __slots__ = ["game_vue", "save_name"]

    def __init__(self, game_vue, save_name = None) -> None:
        self.game_vue = game_vue
        if save_name is None:
            self.save_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        else:
            self.save_name = save_name

    def save(self):
        saves_directory = "saves"
        if not os.path.exists(saves_directory):
            os.makedirs(saves_directory)

        save_dir = os.path.join(saves_directory, self.save_name)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # TODO: finish
        self.save_map()

    def save_map(self):
        map = self.game_vue.map
        signature = [77, 65, 80, 00] # 'MAP_' in ASCII
        with open(f"saves/{self.save_name}/map.exd", "wb") as f:
            for b in signature:
                f.write(struct.pack('B', b))
            
            f.write(struct.pack('i', map.perlin_temperature.seed))
            
            f.write(struct.pack('i', len(map.ores)))
            for chunk_coords, ores in map.ores.items():
                f.write(struct.pack('ii', chunk_coords.x, chunk_coords.y))
                f.write(struct.pack('i', len(ores)))
                for ore_type, ore in ores.items():
                    f.write(struct.pack('B', ore_type.value))
                    f.write(struct.pack('i', len(ore)))
                    for point in ore:
                        f.write(struct.pack('ii', point.x, point.y))
            
            f.write(struct.pack('i', len(map.structures)))
            for chunk_coords, structures in map.structures.items():
                f.write(struct.pack('ii', int(chunk_coords.x), int(chunk_coords.y)))
                f.write(struct.pack('i', len(structures)))
                for structure in structures:
                    f.write(struct.pack('i', structure.structure_type.value))
                    f.write(struct.pack('ii', structure.coords.x, structure.coords.y))
                    f.write(struct.pack('i', len(structure.points)))
                    for point in structure.points:
                        f.write(struct.pack('ii', point.x, point.y))

            f.write(struct.pack('i', len(map.buildings)))
            for building in map.buildings:
                f.write(struct.pack('ii', building.coords.x, building.coords.y))
                f.write(struct.pack('i', len(building.points)))
                for point in building.points:
                    f.write(struct.pack('ii', point.x, point.y))
            
            f.write(struct.pack('i', Perlin.CHUNK_SIZE))
            f.write(struct.pack('i', len(map.perlin_temperature.chunks)))
            for chunk_coords, chunk in map.perlin_temperature.chunks.items():
                f.write(struct.pack('ii', chunk_coords[0], chunk_coords[1]))
                f.write(struct.pack('i', len(chunk)))
                for row in chunk[0]:
                    for value in row:
                        f.write(struct.pack('f', value))

    def load(self):
        # TODO: finish
        #self.load_map()
        pass

    def load_map(self):
        signature = [77, 65, 80, 00] # 'MAP_' in ASCII
        with open(f"saves/{self.save_name}/map.exd", "rb") as f:
            file_signature = list(struct.unpack('BBBB', f.read(4)))
            if file_signature != signature:
                raise ValueError("Invalid file format")
            
            seed = struct.unpack('i', f.read(4))[0]
            map = Map(seed)
            
            num_ores = struct.unpack('i', f.read(4))[0]
            for _ in range(num_ores):
                chunk_x, chunk_y = struct.unpack('ii', f.read(8))
                num_ores_in_chunk = struct.unpack('i', f.read(4))[0]
                ores = {}
                for _ in range(num_ores_in_chunk):
                    ore_type = OreType(struct.unpack('B', f.read(1))[0])
                    num_points = struct.unpack('i', f.read(4))[0]
                    points = []
                    for _ in range(num_points):
                        point_x, point_y = struct.unpack('ii', f.read(8))
                        points.append(Point(point_x, point_y))
                    ores[ore_type] = points
                map.ores[Point(chunk_x, chunk_y)] = ores
            
            num_structures = struct.unpack('i', f.read(4))[0]
            for _ in range(num_structures):
                chunk_x, chunk_y = struct.unpack('ii', f.read(8))
                num_structures_in_chunk = struct.unpack('i', f.read(4))[0]
                structures = []
                for _ in range(num_structures_in_chunk):
                    structure_type = struct.unpack('i', f.read(4))[0]
                    position_x, position_y = struct.unpack('ii', f.read(8))
                    num_points = struct.unpack('i', f.read(4))[0]
                    points = []
                    for _ in range(num_points):
                        point_x, point_y = struct.unpack('ii', f.read(8))
                        points.append(Point(point_x, point_y))
                    structures.append(Structure(structure_type, Point(position_x, position_y), points))
                map.structures[Point(chunk_x, chunk_y)] = structures
            
            num_buildings = struct.unpack('i', f.read(4))[0]
            for _ in range(num_buildings):
                position_x, position_y = struct.unpack('ii', f.read(8))
                num_points = struct.unpack('i', f.read(4))[0]
                points = []
                for _ in range(num_points):
                    point_x, point_y = struct.unpack('ii', f.read(8))
                    points.append(Point(point_x, point_y))
                map.buildings.append(Building(Point(position_x, position_y), points))
            
            chunk_size = struct.unpack('i', f.read(4))[0]
            num_chunks = struct.unpack('i', f.read(4))[0]
            for _ in range(num_chunks):
                chunk_x, chunk_y = struct.unpack('ii', f.read(8))
                num_rows = chunk_size
                num_cols = chunk_size
                chunk = [[0.0] * num_cols for _ in range(num_rows)]
                for i in range(num_rows):
                    for j in range(num_cols):
                        chunk[i][j] = struct.unpack('f', f.read(4))[0]
                map.perlin.chunks[Point(chunk_x, chunk_y)] = chunk
            
            return map