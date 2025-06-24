from config import *
from core.tile import Tile
from core.building import Building
from core.basegrid import BaseGrid
from core.component import Component
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
                tile.clear_highlight()

    def highlight_tile_at(self, pixel_x, pixel_y, offset_y=0):
        gx, gy = self.screen_to_grid(pixel_x, pixel_y, offset_y)
        if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
            self.grid[gy][gx].highlighted = True

    def place_at(self, pixel_x, pixel_y, offset_y=0, item=None):
        gx, gy = self.screen_to_grid(pixel_x, pixel_y, offset_y)
        if not item or not (0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT):
            return

        w, h = item.size

        # Check if the component fits
        if gx + w > GRID_WIDTH or gy + h > GRID_HEIGHT:
            return

        # Ensure all tiles are buildable and empty
        for y in range(h):
            for x in range(w):
                tile = self.grid[gy + y][gx + x]
                if not tile.is_buildable() or tile.building:
                    return  # Abort placement

        # Create a new instance for this placement
        new_component = Component(item.name, item.color, item.size)

        # Place the component
        for y in range(h):
            for x in range(w):
                self.grid[gy + y][gx + x].building = new_component

    def remove_at(self, pixel_x, pixel_y, offset_y=0):
        gx, gy = self.screen_to_grid(pixel_x, pixel_y, offset_y)
        if not (0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT):
            return

        target_tile = self.grid[gy][gx]
        component = target_tile.building
        if not component:
            return

        w, h = component.size

        # Remove only this instance
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x].building == component:
                    self.grid[y][x].building = None
                    self.grid[y][x].type = "clear"
    
    def extract_blueprint_components(self):
        components = []
        for y, row in enumerate(self.grid):
            for x, tile in enumerate(row):
                if tile.building:
                    components.append({
                        "type": tile.building.name,
                        "pos": (x, y)
                    })
        return components