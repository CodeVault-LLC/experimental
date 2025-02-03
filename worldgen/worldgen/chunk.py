import numpy as np
import noise
from typing import NamedTuple

BuildSettings = NamedTuple('BuildSettings', [
    ('octaves', int),
    ('frequency', float),
    ('amplitude', float),
    ('ocean_threshold', float),
    ('river_threshold', float),
    ('mountain_threshold', float),
])

class Chunk:
    def __init__(self, x: int, z: int, chunk_size: int = 16, world_height: int = 64):
        self.x = x
        self.z = z
        self.chunk_size = chunk_size
        self.world_height = world_height

        self.octaves = 6
        self.frequency = 24.0
        self.amplitude = 28.0
        self.ocean_threshold = 0.5
        self.river_threshold = 0.05
        self.mountain_threshold = 0.7

        self.terrain = np.zeros((chunk_size, chunk_size), dtype=int)

    def build_settings(self, settings: BuildSettings):
        """Set the build settings for this chunk."""
        self.octaves = settings.octaves
        self.frequency = settings.frequency
        self.amplitude = settings.amplitude
        self.ocean_threshold = settings.ocean_threshold
        self.river_threshold = settings.river_threshold
        self.mountain_threshold = settings.mountain_threshold

    def generate(self):
        """Generate terrain for this chunk using Perlin noise."""
        for x in range(self.chunk_size):
            for z in range(self.chunk_size):
                world_x = x + self.x * self.chunk_size
                world_z = z + self.z * self.chunk_size

                # Generate Perlin noise value for this block
                height = int(
                    noise.pnoise2(
                        world_x / self.frequency,
                        world_z / self.frequency,
                        octaves=self.octaves,
                    )
                    * self.amplitude
                    + (self.world_height / 2)
                )

                # Determine biome based on height
                if height < self.ocean_threshold * self.world_height:
                    self.terrain[x, z] = 0  # Ocean
                elif abs(height - (self.world_height / 2)) < self.river_threshold * self.world_height:
                    self.terrain[x, z] = 1  # River
                elif height > self.mountain_threshold * self.world_height:
                    self.terrain[x, z] = 3  # Mountain
                else:
                    self.terrain[x, z] = 2  # Grassland

    def get_block(self, x: int, z: int) -> int:
        """Get the block type at a specific position in the chunk."""
        return self.terrain[x, z]
