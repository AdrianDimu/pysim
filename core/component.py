import pygame
from config import TILE_SIZE

class Component:
    def __init__(self, name, color, size=(1, 1)):
        self.name = name
        self.color = color
        self.size = size  # (width, height)
    
    def draw(self, screen, grid_x, grid_y, cam_x, cam_y, zoom, offset_y):
        tile_px = TILE_SIZE * zoom

        px = grid_x * tile_px - cam_x
        py = grid_y * tile_px - cam_y + offset_y

        width = self.size[0] * tile_px - int(8 * zoom)
        height = self.size[1] * tile_px - int(8 * zoom)
        offset = int(4 * zoom)

        rect = pygame.Rect(
            int(px) + offset,
            int(py) + offset,
            int(width),
            int(height)
        )

        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, (200, 200, 200), rect, 2)  # Optional border for visibility
