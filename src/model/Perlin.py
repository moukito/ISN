import random
import numpy as np
import math

class Perlin:
    __slots__ = ["seed", "octave", "persistence", "lacunarity", "scale", "amplitude", "chunks", "gradients", "permutation", "x_offset", "y_offset"]

    CHUNK_SIZE = 32

    def __init__(self, seed = 1, octave = 1, persistence = 1.0, lacunarity = 1.0, scale = 1.0, amplitude = 1.0) -> None:
        self.seed = seed
        self.octave = octave
        self.persistence = persistence
        self.lacunarity = lacunarity
        self.scale = scale
        self.amplitude = amplitude
        self.chunks = {}
        self.gradients = []
        self.permutation = []

        self.set_seed(seed)

    def set_seed(self, seed):
        random.seed(seed)
        self.x_offset = random.randrange(-100, 100)
        self.y_offset = random.randrange(-100, 100)
        
        self.generate_permutation_table()
        self.generate_gradients()
        
    def generate_permutation_table(self):
        permutation = list(range(256))
        random.shuffle(permutation)
        self.permutation = permutation * 2

    def generate_gradients(self):
        for _ in range(256):
            self.gradients.append((random.uniform(-1, 1), random.uniform(-1, 1)))

    def fade(self, t):
        return 6 * t ** 5 - 15 * t ** 4 + 10 * t ** 3 # t*t*t*(t*(t*6 - 15) + 10)

    def lerp(self, a, b, t):
        return a + t * (b - a)

    def dot_product(self, grad, x, y):
        return grad[0] * x + grad[1] * y

    def noise(self, x, y):
        X = math.floor(x) & 255
        Y = math.floor(y) & 255

        xf = x - math.floor(x)
        yf = y - math.floor(y)

        u = self.fade(xf)
        v = self.fade(yf)

        # Hash coordinates of the 4 corners
        aa = self.permutation[X] + Y
        ab = self.permutation[X] + Y + 1
        ba = self.permutation[X + 1] + Y
        bb = self.permutation[X + 1] + Y + 1

        # Gradient vectors
        g_aa = self.gradients[self.permutation[aa] % 256]
        g_ab = self.gradients[self.permutation[ab] % 256]
        g_ba = self.gradients[self.permutation[ba] % 256]
        g_bb = self.gradients[self.permutation[bb] % 256]

        # Dot products
        n_aa = self.dot_product(g_aa, xf, yf)
        n_ab = self.dot_product(g_ab, xf, yf - 1)
        n_ba = self.dot_product(g_ba, xf - 1, yf)
        n_bb = self.dot_product(g_bb, xf - 1, yf - 1)

        # Interpolation
        x1 = self.lerp(n_aa, n_ba, u)
        x2 = self.lerp(n_ab, n_bb, u)

        return self.lerp(x1, x2, v)

    def generate_chunk(self, x, y):
        chunk = np.empty((self.CHUNK_SIZE, self.CHUNK_SIZE), dtype=float)

        # Set min / max
        max_noise_height = -math.inf
        min_noise_height = +math.inf

        for xi in range(self.CHUNK_SIZE):
            for yi in range(self.CHUNK_SIZE):
                amplitude = self.amplitude
                freq = 1
                noise_height = 0

                for _ in range(self.octave):
                    px = (self.CHUNK_SIZE * x + xi + self.x_offset) / self.scale * freq + self.x_offset
                    py = (self.CHUNK_SIZE * y + yi + self.y_offset) / self.scale * freq + self.y_offset

                    perlin_value = self.noise(px, py)
                    noise_height += perlin_value * amplitude

                    # Increase amp and freq
                    amplitude *= self.persistence
                    freq *= self.lacunarity

                # Adjust min and Max
                if noise_height > max_noise_height:
                    max_noise_height = noise_height
                elif noise_height < min_noise_height:
                    min_noise_height = noise_height

                chunk[xi, yi] = noise_height

        self.chunks[(x, y)] = (chunk, min_noise_height, max_noise_height)
    
    def get_chunk(self, x, y):
        if self.chunks.get((x, y)) == None:
            self.generate_chunk(x, y)

        return self.chunks[(x, y)]
    
    def get_chunk_data(self, x, y):
        if self.chunks.get((x, y)) == None:
            self.generate_chunk(x, y)

        return self.chunks[(x, y)][0]