from config import *
import pygame

class Tile:
    def __init__(self, type_name):
        self.type = type_name
        self.building = None
        self.highlight_mode = None  # "buildable", "invalid", or None

    def is_buildable(self):
        return self.type in {"clear"} and self.building is None

    def is_clear(self):
        return self.building is None

    def get_color(self):
        if self.building is not None:
            base = TILE_TYPES.get("building", (255, 255, 150))  # pale yellow fallback
        else:
            base = TILE_TYPES.get(self.type, (100, 100, 100))

        if self.highlight_mode == "buildable":
            return (180, 255, 180)  # green-ish for valid
        elif self.highlight_mode == "invalid":
            return (255, 150, 150)  # red for invalid

        return base

    def draw(self, screen, grid_x, grid_y, cam_x, cam_y, zoom, offset_y):
        tile_px = TILE_SIZE * zoom
        px = grid_x * tile_px - cam_x
        py = grid_y * tile_px - cam_y + offset_y

        # --- Draw base tile
        color = self.get_color()
        pygame.draw.rect(screen, color, (int(px), int(py), tile_px, tile_px))

        # --- Highlight overlay
        if self.highlight_mode == "buildable":
            overlay = pygame.Surface((tile_px, tile_px), pygame.SRCALPHA)
            overlay.fill((255, 255, 180, 100))  # pale yellow
            screen.blit(overlay, (int(px), int(py)))

        elif self.highlight_mode == "invalid":
            overlay = pygame.Surface((tile_px, tile_px), pygame.SRCALPHA)
            overlay.fill((255, 50, 50, 100))  # translucent red
            screen.blit(overlay, (int(px), int(py)))

        # --- Optional border
        pygame.draw.rect(screen, (200, 200, 200), (int(px), int(py), tile_px, tile_px), 1)

    def clear_highlight(self):
        self.highlight_mode = None