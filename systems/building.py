import pygame
import json
from settings import TILE_SIZE

# Load recipes once globally
with open("data/buildings.json") as f:
    RECIPES = json.load(f)

class Building:
    def __init__(self, name, color, group_id=None):
        self.name = name
        self.color = color
        self.recipe = RECIPES.get(name, {})
        self.timer = 0
        self.active = False
        self.group_id = group_id
        
        # Placeholders for future use
        self.input_buffer = {}
        self.output_buffer = {}

    def draw(self, screen, grid_x, grid_y, cam_x, cam_y, zoom, offset_y):
        tile_px = TILE_SIZE * zoom
        px = grid_x * tile_px - cam_x
        py = grid_y * tile_px - cam_y + offset_y

        size = tile_px - int(8 * zoom)
        offset = int(4 * zoom)

        pygame.draw.rect(
            screen,
            self.color,
            (int(px) + offset, int(py) + offset, size, size)
        )

    def update(self, dt):
        if self.can_process():
            self.timer += dt
            if self.timer >= self.recipe.get("process_time", float("inf")):
                self.process()
                self.timer = 0
        else:
            self.timer = 0

    def can_process(self):
        return bool(self.recipe.get("inputs")) and bool(self.recipe.get("outputs"))

    def process(self):
        print(f"{self.name} processed: {self.recipe.get('inputs')} → {self.recipe.get('outputs')}")
