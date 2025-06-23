import pygame
from config import *
from core.tile import Tile
from core.machine import Machine
from core.basegrid import BaseGrid

class World(BaseGrid):
    def __init__(self):
        super().__init__()

    def generate_grid(self):
        grid = [[Tile("clear") for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        grid[5][5] = Tile("iron_ore")
        grid[6][7] = Tile("coal")
        grid[4][6] = Tile("limestone")
        return grid

    def update(self, dt):
        self.update_camera(dt)

        for row in self.grid:
            for tile in row:
                if tile.building:
                    tile.building.update(dt)

    def draw(self, screen, offset_y=0):
        scaled_tile = TILE_SIZE * self.zoom

        tiles_x = SCREEN_WIDTH // int(scaled_tile) + 2
        tiles_y = SCREEN_HEIGHT // int(scaled_tile) + 2

        start_x_camera = int(self.camera_x // scaled_tile)
        start_y_camera = int(self.camera_y // scaled_tile)

        offset_x_camera = self.camera_x % scaled_tile
        offset_y_camera = self.camera_y % scaled_tile

        for y in range(tiles_y):
            for x in range(tiles_x):
                grid_x = start_x_camera + x
                grid_y = start_y_camera + y

                if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                    tile = self.grid[grid_y][grid_x]
                    color = tile.get_color()
                    if tile.highlighted:
                        color = tuple(min(c + 40, 255) for c in color)

                    px = x * scaled_tile - offset_x_camera
                    py = y * scaled_tile - offset_y_camera + offset_y

                    rect = pygame.Rect(int(px), int(py), int(scaled_tile), int(scaled_tile))
                    pygame.draw.rect(screen, color, rect)

                    if tile.building:
                        tile.building.draw(screen, grid_x, grid_y, self.camera_x, self.camera_y, self.zoom, offset_y)

        # Grid overlay
        self.draw_grid_overlay(screen, tiles_x, tiles_y, offset_x_camera, offset_y_camera, offset_y)

    def clear_highlight(self):
        for row in self.grid:
            for tile in row:
                tile.highlighted = False

    def highlight_tile_at(self, pixel_x, pixel_y, offset_y=0):
        grid_x, grid_y = self.screen_to_grid(pixel_x, pixel_y, offset_y)
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            self.grid[grid_y][grid_x].highlighted = True

    def place_at(self, pixel_x, pixel_y, offset_y=0):
        grid_x, grid_y = self.screen_to_grid(pixel_x, pixel_y, offset_y)
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            tile = self.grid[grid_y][grid_x]
            if tile.is_buildable() and tile.building is None:
                tile.building = Machine("Crusher", (200, 100, 255))
                tile.building.add_input("Iron Ore", 5)
