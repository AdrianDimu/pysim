from config import *
from core.tile import Tile
from core.machine import Machine
from core.basegrid import BaseGrid
import pygame

class BuildGrid(BaseGrid):
    def __init__(self):
        super().__init__()

    def generate_grid(self):
        return [[Tile("clear") for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    def update(self, dt, offset_top=0, offset_bottom=0):
        self.update_camera(dt, offset_top=offset_top, offset_bottom=offset_bottom)

    def draw(self, screen, offset_y=0):
        def draw_tile(screen, tile, gx, gy, x, y, scaled_tile, offset_x, offset_y_camera, offset_top):
            color = tile.get_color()
            px = x * scaled_tile - offset_x
            py = y * scaled_tile - offset_y_camera + offset_top
            rect = pygame.Rect(int(px), int(py), int(scaled_tile), int(scaled_tile))
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)

            if tile.building:
                tile.building.draw(screen, gx, gy, self.camera_x, self.camera_y, self.zoom, offset_top)

        self.draw_tiles_and_grid(screen, offset_top=offset_y, draw_tile_fn=draw_tile)


    def clear_highlight(self):
        for row in self.grid:
            for tile in row:
                tile.highlighted = False

    def highlight_tile_at(self, pixel_x, pixel_y, offset_y=0):
        gx, gy = self.screen_to_grid(pixel_x, pixel_y, offset_y)
        if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
            self.grid[gy][gx].highlighted = True

    def place_at(self, pixel_x, pixel_y, offset_y=0):
        print("[BuildGrid] Placement ignored – components will be implemented later.")

    def remove_at(self, pixel_x, pixel_y, offset_y=0):
        print("[BuildGrid] Removal ignored – components will be implemented later.")