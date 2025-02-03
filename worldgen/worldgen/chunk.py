import numpy as np
import noise

# Constants
CHUNK_SIZE = 16  # Size of each chunk (16x16 blocks, like Minecraft)
WORLD_HEIGHT = 64  # Maximum height of the world
OCTAVES = 6  # Number of layers of noise for terrain detail
FREQUENCY = 24.0  # Controls the smoothness of terrain
AMPLITUDE = 28.0  # Controls the height of terrain

# Biome thresholds
OCEAN_THRESHOLD = 0.5
RIVER_THRESHOLD = 0.05
MOUNTAIN_THRESHOLD = 0.7

class Chunk:
    def __init__(self, x: int, z: int, chunk_size: int = 16, world_height: int = 64):
        self.x = x
        self.z = z
        self.chunk_size = chunk_size
        self.world_height = world_height

        self.terrain = np.zeros((chunk_size, chunk_size), dtype=int)

    def generate(self):
        """Generate terrain for this chunk using Perlin noise."""
        for x in range(self.chunk_size):
            for z in range(self.chunk_size):
                world_x = x + self.x * self.chunk_size
                world_z = z + self.z * self.chunk_size

                # Generate Perlin noise value for this block
                height = int(
                    noise.pnoise2(
                        world_x / FREQUENCY,
                        world_z / FREQUENCY,
                        octaves=OCTAVES,
                    )
                    * AMPLITUDE
                    + (WORLD_HEIGHT / 2)
                )

                # Determine biome based on height
                if height < OCEAN_THRESHOLD * WORLD_HEIGHT:
                    self.terrain[x, z] = 0  # Ocean
                elif abs(height - (WORLD_HEIGHT / 2)) < RIVER_THRESHOLD * WORLD_HEIGHT:
                    self.terrain[x, z] = 1  # River
                elif height > MOUNTAIN_THRESHOLD * WORLD_HEIGHT:
                    self.terrain[x, z] = 3  # Mountain
                else:
                    self.terrain[x, z] = 2  # Grassland

    def get_block(self, x: int, z: int) -> int:
        """Get the block type at a specific position in the chunk."""
        return self.terrain[x, z]
