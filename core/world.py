import pygame
from config import *
from core.tile import Tile
from core.machine import Machine

class World:
    def __init__(self):
        self.grid = [
            [Tile("clear") for _ in range(GRID_WIDTH)]
            for _ in range(GRID_HEIGHT)
        ]
        # Add resource tiles
        self.grid[5][5] = Tile("iron_ore")
        self.grid[6][7] = Tile("coal")
        self.grid[4][6] = Tile("limestone")

        self.camera_x = 0
        self.camera_y = 0

        self.camera_ax = 0
        self.camera_ay = 0

        self.camera_vx = 0
        self.camera_vy = 0

        self.scroll_accel = 2000  # pixels per second^2
        self.scroll_max_speed = 600  # max velocity in px/s

        self.zoom = 1.0  # 1.0 = 100%
        self.min_zoom = 0.5
        self.max_zoom = 2.0

    def screen_to_grid(self, pixel_x, pixel_y, offset_y=0):
        tile_px = TILE_SIZE * self.zoom
        world_x = self.camera_x + pixel_x
        world_y = self.camera_y + (pixel_y - offset_y)
        return int(world_x // tile_px), int(world_y // tile_px)
    
    def clamp_camera(self):
        tile_px = TILE_SIZE * self.zoom
        view_w = SCREEN_WIDTH
        view_h = SCREEN_HEIGHT
        world_w = GRID_WIDTH * tile_px
        world_h = GRID_HEIGHT * tile_px

        # Allow ~1 tile of negative margin
        margin = tile_px

        max_x = max(-margin, world_w - view_w + margin)
        max_y = max(-margin, world_h - view_h + margin)

        self.camera_x = max(-margin, min(self.camera_x, max_x))
        self.camera_y = max(-margin, min(self.camera_y, max_y))

    def draw(self, screen, offset_y=0):
        scaled_tile = TILE_SIZE * self.zoom  # float!

        # Dynamically calculate how many tiles fit on screen
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
                    color = TILE_TYPES[tile.type]
                    if tile.highlighted:
                        color = tuple(min(c + 40, 255) for c in color)

                    px = x * scaled_tile - offset_x_camera
                    py = y * scaled_tile - offset_y_camera + offset_y

                    rect = pygame.Rect(int(px), int(py), int(scaled_tile), int(scaled_tile))
                    pygame.draw.rect(screen, color, rect)

                    if tile.building:
                        tile.building.draw(screen, grid_x, grid_y, self.camera_x, self.camera_y, self.zoom, offset_y)
        
        # --- Draw grid lines overlay ---
        # Vertical lines
        for x in range(tiles_x + 1):
            px = int(x * scaled_tile - offset_x_camera)
            pygame.draw.line(screen, BLUEPRINT_BG, (px, offset_y), (px, SCREEN_HEIGHT))

        # Horizontal lines
        for y in range(tiles_y + 1):
            py = int(y * scaled_tile - offset_y_camera + offset_y)
            pygame.draw.line(screen, BLUEPRINT_BG, (0, py), (SCREEN_WIDTH, py))

    def move_camera(self, dx, dy):
        move_px = self.camera_speed
        tile_px = TILE_SIZE * self.zoom

        # Update camera position
        self.camera_x += dx * move_px
        self.camera_y += dy * move_px

        # Calculate max scroll with 1 tile of margin
        max_x = GRID_WIDTH * tile_px - SCREEN_WIDTH + tile_px
        max_y = GRID_HEIGHT * tile_px - SCREEN_HEIGHT + tile_px

        self.camera_x = max(-tile_px, min(self.camera_x, max_x))
        self.camera_y = max(-tile_px, min(self.camera_y, max_y))

        self.clamp_camera()

    def adjust_zoom(self, delta, mouse_x, mouse_y, offset_y=0):
        # Defined zoom levels
        zoom_levels = [0.5, 1.0, 1.5, 2.0]

        # Find the closest zoom level to current
        closest_zoom = min(zoom_levels, key=lambda z: abs(z - self.zoom))
        current_index = zoom_levels.index(closest_zoom)

        new_index = current_index + int(delta / 0.5)
        new_index = max(0, min(new_index, len(zoom_levels) - 1))
        new_zoom = zoom_levels[new_index]

        if new_zoom == self.zoom:
            return  # No change

        # 1. Convert screen position to world coordinate
        world_x = self.camera_x + mouse_x
        world_y = self.camera_y + (mouse_y - offset_y)

        # 2. Find ratio of that point relative to current zoom
        ratio_x = world_x / self.zoom
        ratio_y = world_y / self.zoom

        # 3. Apply new zoom and set camera so that mouse stays on same world tile
        self.zoom = new_zoom
        self.camera_x = ratio_x * new_zoom - mouse_x
        self.camera_y = ratio_y * new_zoom - (mouse_y - offset_y)

        # Now enforce that camera stays within allowed bounds
        self.clamp_camera()

    def clear_highlight(self):
        for row in self.grid:
            for tile in row:
                tile.highlighted = False

    def highlight_tile_at(self, pixel_x, pixel_y, offset_y):
        grid_x, grid_y = self.screen_to_grid(pixel_x, pixel_y, offset_y)
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            self.grid[grid_y][grid_x].highlighted = True

    def place_machine_at(self, pixel_x, pixel_y, offset_y):
        grid_x, grid_y = self.screen_to_grid(pixel_x, pixel_y, offset_y)
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            tile = self.grid[grid_y][grid_x]
            if tile.is_buildable() and tile.building is None:
                tile.building = Machine("Crusher", (200, 100, 255))
                tile.building.add_input("Iron Ore", 5)

    def update(self, dt):
        seconds = dt / 1000

        # 1. Accelerate
        self.camera_vx += self.camera_ax * seconds
        self.camera_vy += self.camera_ay * seconds

        # 2. Clamp velocity
        self.camera_vx = max(-self.scroll_max_speed, min(self.camera_vx, self.scroll_max_speed))
        self.camera_vy = max(-self.scroll_max_speed, min(self.camera_vy, self.scroll_max_speed))

        # 3. Normalize diagonal velocity
        speed = (self.camera_vx ** 2 + self.camera_vy ** 2) ** 0.5
        if speed > self.scroll_max_speed:
            scale = self.scroll_max_speed / speed
            self.camera_vx *= scale
            self.camera_vy *= scale

        # 4. Add friction
        friction = 0.85
        if self.camera_ax == 0:
            self.camera_vx *= friction
        if self.camera_ay == 0:
            self.camera_vy *= friction

        if abs(self.camera_vx) < 5:
            self.camera_vx = 0
        if abs(self.camera_vy) < 5:
            self.camera_vy = 0

        # 5. Apply movement
        self.camera_x += self.camera_vx * seconds
        self.camera_y += self.camera_vy * seconds

        # 6. Clamp camera
        self.clamp_camera()

        # 7. Update buildings
        for row in self.grid:
            for tile in row:
                if tile.building:
                    tile.building.update(dt)