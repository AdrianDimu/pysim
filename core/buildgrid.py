import pygame
from config import *
from core.tile import Tile
from core.machine import Machine
from core.world import World

class BuildGrid(World):
    def __init__(self):
        super().__init__()
        # You can override specific init values if needed
        for row in self.grid:
            for tile in row:
                tile.type = "clear"

        self.camera_x, self.camera_y = 0, 0  
        self.camera_ax, self.camera_ay = 0, 0  
        self.camera_vx, self.camera_vy = 0, 0  
        self.scroll_accel = 2000  
        self.scroll_max_speed = 600

        self.zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 2.0

    def screen_to_grid(self, pixel_x, pixel_y):
        tile_px = TILE_SIZE * self.zoom
        return int((self.camera_x + pixel_x) // tile_px), int((self.camera_y + pixel_y) // tile_px)

    def clamp_camera(self):
        tile_px = TILE_SIZE * self.zoom
        world_w = GRID_WIDTH * tile_px
        world_h = GRID_HEIGHT * tile_px
        view_w = SCREEN_WIDTH
        view_h = SCREEN_HEIGHT
        margin = tile_px

        max_x = max(-margin, world_w - view_w + margin)
        max_y = max(-margin, world_h - view_h + margin)

        self.camera_x = max(-margin, min(self.camera_x, max_x))
        self.camera_y = max(-margin, min(self.camera_y, max_y))

    def adjust_zoom(self, delta, mouse_x, mouse_y):
        old_zoom = self.zoom
        new_zoom = max(self.min_zoom, min(self.zoom + delta, self.max_zoom))

        if new_zoom == self.zoom:
            return

        world_x = self.camera_x + mouse_x
        world_y = self.camera_y + mouse_y

        ratio_x = world_x / old_zoom
        ratio_y = world_y / old_zoom

        self.zoom = new_zoom
        self.camera_x = ratio_x * new_zoom - mouse_x
        self.camera_y = ratio_y * new_zoom - mouse_y

    def draw(self, screen):
        tile_px = TILE_SIZE * self.zoom
        tiles_x = SCREEN_WIDTH // int(tile_px) + 2
        tiles_y = SCREEN_HEIGHT // int(tile_px) + 2
        start_x = int(self.camera_x // tile_px)
        start_y = int(self.camera_y // tile_px)
        offset_x = self.camera_x % tile_px
        offset_y = self.camera_y % tile_px

        for y in range(tiles_y):
            for x in range(tiles_x):
                gx, gy = start_x + x, start_y + y
                if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                    tile = self.grid[gy][gx]
                    color = TILE_TYPES[tile.type]
                    if tile.highlighted:
                        color = tuple(min(c + 40, 255) for c in color)

                    rect = pygame.Rect(
                        x * tile_px - offset_x,
                        y * tile_px - offset_y,
                        tile_px, tile_px
                    )
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, (200, 200, 200), rect, 1)

                    if tile.building:
                        tile.building.draw(screen, gx, gy, self.camera_x, self.camera_y, self.zoom, offset_y=0)

    def clear_highlight(self):
        for row in self.grid:
            for tile in row:
                tile.highlighted = False

    def highlight_tile_at(self, pixel_x, pixel_y):
        gx, gy = self.screen_to_grid(pixel_x, pixel_y)
        if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
            self.grid[gy][gx].highlighted = True

    def place_machine_at(self, pixel_x, pixel_y):
        gx, gy = self.screen_to_grid(pixel_x, pixel_y)
        if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
            tile = self.grid[gy][gx]
            if tile.is_buildable() and tile.building is None:
                tile.building = Machine("Drill", (100, 200, 255))

    def update(self, dt):
        seconds = dt / 1000

        # Accelerate
        self.camera_vx += self.camera_ax * seconds
        self.camera_vy += self.camera_ay * seconds

        # Clamp velocity
        self.camera_vx = max(-self.scroll_max_speed, min(self.camera_vx, self.scroll_max_speed))
        self.camera_vy = max(-self.scroll_max_speed, min(self.camera_vy, self.scroll_max_speed))

        # Normalize diagonal movement
        speed = (self.camera_vx ** 2 + self.camera_vy ** 2) ** 0.5
        if speed > self.scroll_max_speed:
            scale = self.scroll_max_speed / speed
            self.camera_vx *= scale
            self.camera_vy *= scale

        # Friction
        friction = 0.85
        if self.camera_ax == 0:
            self.camera_vx *= friction
        if self.camera_ay == 0:
            self.camera_vy *= friction

        if abs(self.camera_vx) < 5: self.camera_vx = 0
        if abs(self.camera_vy) < 5: self.camera_vy = 0

        # Apply movement
        self.camera_x += self.camera_vx * seconds
        self.camera_y += self.camera_vy * seconds

        self.clamp_camera()
