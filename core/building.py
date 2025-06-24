import pygame
import json
from config import TILE_SIZE
from core.inventory import Inventory

# Load recipes once globally
with open("data/buildings.json") as f:
    RECIPES = json.load(f)

class Building:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.recipe = RECIPES[name]
        self.input_buffer = {}
        self.output_buffer = {}
        self.timer = 0
        self.active = False
        self.input_inventory = Inventory()
        self.output_inventory = Inventory()

    def draw(self, screen, grid_x, grid_y, cam_x, cam_y, zoom, offset_y):
        tile_px = TILE_SIZE * zoom  # must match tile size exactly

        # Same pixel placement logic as tile rendering
        px = grid_x * tile_px - cam_x
        py = grid_y * tile_px - cam_y + offset_y

        size = tile_px - int(8 * zoom)
        offset = int(4 * zoom)

        pygame.draw.rect(
            screen,
            self.color,
            (int(px) + offset, int(py) + offset, size, size)
        )
    
    def add_input(self, item_name, amount=1):
        self.input_inventory.add(item_name, amount)

    def update(self, dt):
        if self.can_process():
            self.timer += dt
            if self.timer >= self.recipe["process_time"]:
                self.process()
                self.timer = 0
        else:
            self.timer = 0  # reset if missing inputs

    def can_process(self):
        for item, amount in self.recipe["inputs"].items():
            if not self.input_inventory.has(item, amount):
                return False
        return True

    def process(self):
        for item, amount in self.recipe["inputs"].items():
            self.input_inventory.remove(item, amount)
        for item, amount in self.recipe["outputs"].items():
            self.output_inventory.add(item, amount)
        print(f"{self.name} processed: {self.recipe['inputs']} → {self.recipe['outputs']}")