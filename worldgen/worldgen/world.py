from typing import Dict, Tuple
from .chunk import Chunk, BuildSettings

# Constants
BLOCKS = {
    0: "Ocean",
    1: "River",
    2: "Grassland",
    3: "Mountain",
}

class World:
    """Class representing the game world, composed of multiple chunks. Handles chunk generation and block retrieval."""
    def __init__(self, build_settings: BuildSettings, chunk_size: int = 16):
        self.chunk_size = chunk_size
        self.build_settings = build_settings

        self.chunks: Dict[Tuple[int, int], Chunk] = {}  # Dictionary to store generated chunks

    def get_chunk(self, x: int, z: int) -> Chunk:
        """Get or generate a chunk at the specified chunk coordinates."""
        if (x, z) not in self.chunks:
            self.generate_chunk(x, z)
        return self.chunks[(x, z)]

    def generate_chunk(self, x: int, z: int):
        """Generate a chunk at the specified chunk coordinates."""
        chunk = Chunk(x, z)
        if self.build_settings is not None:
            chunk.build_settings(self.build_settings)
        chunk.generate()
        self.chunks[(x, z)] = chunk

    def get_block(self, world_x: int, world_z: int) -> int:
        """Get the block type at a specific world coordinate."""
        chunk_x = world_x // self.chunk_size
        chunk_z = world_z // self.chunk_size
        chunk = self.get_chunk(chunk_x, chunk_z)
        local_x = world_x % self.chunk_size
        local_z = world_z % self.chunk_size
        return chunk.get_block(local_x, local_z)

    def get_prettified_block(self, world_x: int, world_z: int) -> str:
        """Get the prettified block type at a specific world coordinate (e.g. 'Ocean', 'River', 'Grassland', 'Mountain')"""
        block = self.get_block(world_x, world_z)
        return BLOCKS[block]
