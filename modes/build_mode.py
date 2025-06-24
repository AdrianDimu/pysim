from settings import *
from systems.tile import Tile
from systems.building import Building
from systems.basegrid import BaseGrid
from systems.component import Component
import pygame
import copy

class BuildGrid(BaseGrid):
    def __init__(self):
        super().__init__()

    def generate_grid(self):
        return [[Tile(tile_type="basic") for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    def update(self, dt, offset_top=0, offset_bottom=0):
        self.update_camera(dt, offset_top=offset_top, offset_bottom=offset_bottom)

    def draw(self, screen, offset_y=0):
        def draw_tile_fn(screen, tile, gx, gy, x, y, scaled_tile, offset_x, offset_y, offset_top):
            px = x * scaled_tile - offset_x
            py = y * scaled_tile - offset_y + offset_top
            color = tile.get_color()
            pygame.draw.rect(screen, color, (px, py, scaled_tile, scaled_tile))

            if tile.building:  # In build mode, 'building' = component
                size = scaled_tile - int(8 * self.zoom)
                offset = int(4 * self.zoom)
                surf = pygame.Surface((size, size), pygame.SRCALPHA)
                surf.fill(tile.building.color + (255,))
                screen.blit(surf, (int(px) + offset, int(py) + offset))

        self.draw_tiles_and_grid(screen, offset_top=offset_y, draw_tile_fn=draw_tile_fn)

    def clear_highlight(self):
        for row in self.grid:
            for tile in row:
                tile.clear_highlight()

    def highlight_tile_at(self, pixel_x, pixel_y, offset_y=0):
        gx, gy = self.screen_to_grid(pixel_x, pixel_y, offset_y)
        if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
            self.grid[gy][gx].highlighted = True

    def place_at(self, pixel_x, pixel_y, offset_y=0, item=None):
        print(f"[PLACE] Attempting to place: {item.name if item else 'None'}")
        if not isinstance(item, Component):
            return

        grid_x, grid_y = self.screen_to_grid(pixel_x, pixel_y, offset_y)
        print(f"[PLACE] Grid position: {grid_x}, {grid_y}")

        comp_w, comp_h = item.size
        if grid_x + comp_w > GRID_WIDTH or grid_y + comp_h > GRID_HEIGHT:
            print("[PLACE] Out of bounds!")
            return

        for dy in range(comp_h):
            for dx in range(comp_w):
                tile = self.grid[grid_y + dy][grid_x + dx]
                if not tile.is_placeable_by(item, strict=False):
                    print(f"[PLACE] Tile at ({grid_x+dx}, {grid_y+dy}) not placeable.")
                    return

        print("[PLACE] Placing component...")
        instance = copy.deepcopy(item)
        for dy in range(comp_h):
            for dx in range(comp_w):
                self.grid[grid_y + dy][grid_x + dx].set_occupied(instance)

    def remove_at(self, pixel_x, pixel_y, offset_y=0):
        gx, gy = self.screen_to_grid(pixel_x, pixel_y, offset_y)
        if not (0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT):
            return

        target_tile = self.grid[gy][gx]
        target_component = target_tile.building
        if not target_component:
            return

        comp_w, comp_h = target_component.size

        for dy in range(comp_h):
            for dx in range(comp_w):
                tx, ty = gx - dx, gy - dy
                if 0 <= tx < GRID_WIDTH and 0 <= ty < GRID_HEIGHT:
                    tile = self.grid[ty][tx]
                    if tile.building == target_component:
                        tile.clear()

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
