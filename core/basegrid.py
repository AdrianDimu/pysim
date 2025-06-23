import abc
import pygame
from config import *

class BaseGrid(abc.ABC):
    def __init__(self):
        self.camera_x = 0
        self.camera_y = 0
        self.camera_ax = 0
        self.camera_ay = 0
        self.camera_vx = 0
        self.camera_vy = 0

        self.scroll_accel = 2000
        self.scroll_max_speed = 600

        self.zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 2.0
        
        self.grid = self.generate_grid()

    def screen_to_grid(self, pixel_x, pixel_y, offset_y=0):
        tile_px = TILE_SIZE * self.zoom
        world_x = self.camera_x + pixel_x
        world_y = self.camera_y + (pixel_y - offset_y)
        return int(world_x // tile_px), int(world_y // tile_px)

    def clamp_camera(self, offset_top=0, offset_bottom=0):
        tile_px = TILE_SIZE * self.zoom
        view_w = SCREEN_WIDTH
        view_h = SCREEN_HEIGHT - offset_top - offset_bottom
        world_w = GRID_WIDTH * tile_px
        world_h = GRID_HEIGHT * tile_px
        margin = tile_px

        max_x = max(-margin, world_w - view_w + margin)
        max_y = max(-margin, world_h - view_h + margin)

        self.camera_x = max(-margin, min(self.camera_x, max_x))
        self.camera_y = max(-margin, min(self.camera_y, max_y))

    def adjust_zoom(self, delta, mouse_x, mouse_y, offset_top=0, offset_bottom=0):
        zoom_levels = [0.5, 1.0, 1.5, 2.0]
        closest_zoom = min(zoom_levels, key=lambda z: abs(z - self.zoom))
        current_index = zoom_levels.index(closest_zoom)
        new_index = max(0, min(current_index + int(delta / 0.5), len(zoom_levels) - 1))
        new_zoom = zoom_levels[new_index]
        if new_zoom == self.zoom:
            return

        world_x = self.camera_x + mouse_x
        world_y = self.camera_y + (mouse_y - offset_top)

        ratio_x = world_x / self.zoom
        ratio_y = world_y / self.zoom

        self.zoom = new_zoom
        self.camera_x = ratio_x * new_zoom - mouse_x
        self.camera_y = ratio_y * new_zoom - (mouse_y - offset_top)

        self.clamp_camera(offset_top=offset_top, offset_bottom=offset_bottom)

    def update_camera(self, dt, offset_top=0, offset_bottom=0):
        seconds = dt / 1000
        self.camera_vx += self.camera_ax * seconds
        self.camera_vy += self.camera_ay * seconds

        self.camera_vx = max(-self.scroll_max_speed, min(self.camera_vx, self.scroll_max_speed))
        self.camera_vy = max(-self.scroll_max_speed, min(self.camera_vy, self.scroll_max_speed))

        speed = (self.camera_vx ** 2 + self.camera_vy ** 2) ** 0.5
        if speed > self.scroll_max_speed:
            scale = self.scroll_max_speed / speed
            self.camera_vx *= scale
            self.camera_vy *= scale

        friction = 0.85
        if self.camera_ax == 0: self.camera_vx *= friction
        if self.camera_ay == 0: self.camera_vy *= friction
        if abs(self.camera_vx) < 5: self.camera_vx = 0
        if abs(self.camera_vy) < 5: self.camera_vy = 0

        self.camera_x += self.camera_vx * seconds
        self.camera_y += self.camera_vy * seconds
        self.clamp_camera(offset_top=offset_top, offset_bottom=offset_bottom)

    def draw_grid_overlay(self, screen, tiles_x, tiles_y, offset_x, offset_y, gui_offset=0):
        scaled_tile = TILE_SIZE * self.zoom

        # Vertical lines
        for x in range(tiles_x + 1):
            px = int(x * scaled_tile - offset_x)
            pygame.draw.line(screen, BLUEPRINT_BG, (px, gui_offset), (px, SCREEN_HEIGHT))

        # Horizontal lines
        for y in range(tiles_y + 1):
            py = int(y * scaled_tile - offset_y + gui_offset)
            pygame.draw.line(screen, BLUEPRINT_BG, (0, py), (SCREEN_WIDTH, py))

    def draw_tiles_and_grid(self, screen, offset_top=0, offset_bottom=0, draw_tile_fn=None):
        scaled_tile = TILE_SIZE * self.zoom
        view_w = SCREEN_WIDTH
        view_h = SCREEN_HEIGHT - offset_top - offset_bottom

        tiles_x = view_w // int(scaled_tile) + 2
        tiles_y = view_h // int(scaled_tile) + 2

        start_x = int(self.camera_x // scaled_tile)
        start_y = int(self.camera_y // scaled_tile)

        offset_x = self.camera_x % scaled_tile
        offset_y = self.camera_y % scaled_tile

        for y in range(tiles_y):
            for x in range(tiles_x):
                gx = start_x + x
                gy = start_y + y
                if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                    tile = self.grid[gy][gx]
                    if draw_tile_fn:
                        draw_tile_fn(
                            screen, tile, gx, gy, x, y,
                            scaled_tile, offset_x, offset_y, offset_top
                        )

        self.draw_grid_overlay(screen, tiles_x, tiles_y, offset_x, offset_y, gui_offset=offset_top)

    @abc.abstractmethod
    def generate_grid(self): pass
    
    @abc.abstractmethod
    def draw(self, screen, offset_y=0): pass

    @abc.abstractmethod
    def update(self, dt, offset_top=0, offset_bottom=0): pass

    @abc.abstractmethod
    def clear_highlight(self): pass

    @abc.abstractmethod
    def highlight_tile_at(self, pixel_x, pixel_y, offset_y=0): pass

    @abc.abstractmethod
    def place_at(self, pixel_x, pixel_y, offset_y=0): pass