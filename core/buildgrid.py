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

    def update(self, dt):
        self.update_camera(dt)

    def draw(self, screen, offset_y=0):
        scaled_tile = TILE_SIZE * self.zoom
        tiles_x = SCREEN_WIDTH // int(scaled_tile) + 2
        tiles_y = SCREEN_HEIGHT // int(scaled_tile) + 2

        start_x = int(self.camera_x // scaled_tile)
        start_y = int(self.camera_y // scaled_tile)

        offset_x = self.camera_x % scaled_tile
        offset_y_camera = self.camera_y % scaled_tile

        for y in range(tiles_y):
            for x in range(tiles_x):
                gx = start_x + x
                gy = start_y + y
                if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                    tile = self.grid[gy][gx]
                    color = tile.get_color()

                    rect = pygame.Rect(
                        int(x * scaled_tile - offset_x),
                        int(y * scaled_tile - offset_y_camera + offset_y),
                        int(scaled_tile), int(scaled_tile)
                    )
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, (200, 200, 200), rect, 1)

                    if tile.building:
                        tile.building.draw(screen, gx, gy, self.camera_x, self.camera_y, self.zoom, offset_y)

        self.draw_grid_overlay(screen, tiles_x, tiles_y, offset_x, offset_y_camera + offset_y)


    def clear_highlight(self):
        for row in self.grid:
            for tile in row:
                tile.highlighted = False

    def highlight_tile_at(self, pixel_x, pixel_y, offset_y=0):
        gx, gy = self.screen_to_grid(pixel_x, pixel_y, offset_y)
        if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
            self.grid[gy][gx].highlighted = True

    def place_at(self, pixel_x, pixel_y, offset_y=0):
        gx, gy = self.screen_to_grid(pixel_x, pixel_y, offset_y)
        if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
            tile = self.grid[gy][gx]
            if tile.is_buildable() and tile.building is None:
                tile.building = Machine("Drill", (100, 200, 255))