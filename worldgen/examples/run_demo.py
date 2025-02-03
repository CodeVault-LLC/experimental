import pygame
from worldgen.world import World
from worldgen.chunk import BuildSettings

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLOCK_SIZE = 10  # Size of each block in pixels
COLORS = {
    0: (0, 0, 255),  # Ocean
    1: (0, 0, 150),  # River
    2: (34, 139, 34),  # Grass
    3: (139, 69, 19),  # Mountain
}

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        build_settings = BuildSettings(
            octaves=6,
            frequency=24.0,
            amplitude=28.0,
            ocean_threshold=0.5,
            river_threshold=0.05,
            mountain_threshold=0.7,
        )

        self.world = World(build_settings=build_settings)
        self.camera_x = 0
        self.camera_y = 0
        self.dragging = False
        self.last_mouse_pos = (0, 0)

    def run(self):
        """Main game loop."""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        self.dragging = True
                        self.last_mouse_pos = event.pos
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left mouse button
                        self.dragging = False
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        dx = event.pos[0] - self.last_mouse_pos[0]
                        dy = event.pos[1] - self.last_mouse_pos[1]
                        self.camera_x -= dx // BLOCK_SIZE
                        self.camera_y -= dy // BLOCK_SIZE
                        self.last_mouse_pos = event.pos

            self.screen.fill((0, 0, 0))  # Clear screen
            self.render_world()
            pygame.display.flip()
            self.clock.tick(60)  # Cap at 60 FPS

        pygame.quit()

    def render_world(self):
        """Render the world based on the camera position."""
        for x in range(SCREEN_WIDTH // BLOCK_SIZE):
            for y in range(SCREEN_HEIGHT // BLOCK_SIZE):
                world_x = x + self.camera_x
                world_y = y + self.camera_y
                block_type = self.world.get_block(world_x, world_y)
                color = COLORS.get(block_type, (0, 0, 0))  # Default to black if block type is unknown
                pygame.draw.rect(
                    self.screen,
                    color,
                    (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                )

if __name__ == "__main__":
    game = Game()
    game.run()
