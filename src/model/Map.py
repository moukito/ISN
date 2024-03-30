from enum import Enum

from Perlin import Perlin

import matplotlib.pyplot as plt

class Biomes(Enum):
    PLAIN = 1
    VOLCANO = 2
    LAVA = 3
    SNOW = 4
    MUSHROOM_FOREST = 5


class Map:
    __slots__ = ["perlin"]

    def __init__(self, seed = 1) -> None:
        self.perlin = Perlin(seed, 4, 2, 2, 100, 1, 64)
        
        # Perlin tests
        if seed == 0:
            a = self.perlin.get_chunk(0, 0)
            b = self.perlin.get_chunk(1, 0)
            c = self.perlin.get_chunk(0, 1)
            d = self.perlin.get_chunk(1, 1)

            print(a[1], a[2])

            fig, ax = plt.subplots()
            ax.imshow(a[0])
            fig, ax = plt.subplots()
            ax.imshow(b[0])
            fig, ax = plt.subplots()
            ax.imshow(c[0])
            fig, ax = plt.subplots()
            ax.imshow(d[0])
            plt.show()

if __name__ == "__main__":
    map = Map(0)