from typing import Dict, Tuple
from .chunk import Chunk

class World:
    def __init__(self, chunk_size: int = 16):
        self.chunk_size = chunk_size

        self.chunks: Dict[Tuple[int, int], Chunk] = {}  # Dictionary to store generated chunks

    def get_chunk(self, x: int, z: int) -> Chunk:
        """Get or generate a chunk at the specified chunk coordinates."""
        if (x, z) not in self.chunks:
            chunk = Chunk(x, z)
            chunk.generate()
            self.chunks[(x, z)] = chunk
        return self.chunks[(x, z)]

    def get_block(self, world_x: int, world_z: int) -> int:
        """Get the block type at a specific world coordinate."""
        chunk_x = world_x // self.chunk_size
        chunk_z = world_z // self.chunk_size
        chunk = self.get_chunk(chunk_x, chunk_z)
        local_x = world_x % self.chunk_size
        local_z = world_z % self.chunk_size
        return chunk.get_block(local_x, local_z)
