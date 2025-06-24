import json, os
import pygame
from systems.component import Component
from systems.building import Building
from settings import TILE_SIZE, GRID_WIDTH, GRID_HEIGHT
import uuid

with open(os.path.join("data", "components.json")) as f:
    COMPONENT_DATA = json.load(f)

class Blueprint:
    def __init__(self, name, components):
        self.name = name
        self.components = components  # list of {"type": str, "pos": (x, y)}

    def to_dict(self):
        return {
            "components": [
                {"type": comp["type"], "pos": list(comp["pos"])}
                for comp in self.components
            ]
        }

    def can_place_at(self, grid, grid_x, grid_y):
        for comp in self.components:
            cx, cy = comp["pos"]
            tx, ty = grid_x + cx, grid_y + cy

            if not (0 <= tx < GRID_WIDTH and 0 <= ty < GRID_HEIGHT):
                return False

            tile = grid[ty][tx]
            comp_data = COMPONENT_DATA.get(comp["type"], {})
            color = tuple(comp_data.get("color", (100, 100, 100)))
            size = tuple(comp_data.get("size", [1, 1]))
            valid_tile_types = comp_data.get("valid_tile_types", [])
            valid_subtypes = comp_data.get("valid_subtypes", [])

            virtual_comp = Component(comp["type"], color, size, valid_tile_types, valid_subtypes)

            if not tile.is_placeable_by(virtual_comp):
                return False

        return True

    def instantiate(self, grid, grid_x, grid_y):
        if not self.can_place_at(grid, grid_x, grid_y):
            print(f"[Blueprint] Invalid placement at ({grid_x}, {grid_y})")
            return
        
        group_id = str(uuid.uuid4())  # unique per blueprint placement

        for comp in self.components:
            cx, cy = comp["pos"]
            tx = grid_x + cx
            ty = grid_y + cy

            if 0 <= tx < GRID_WIDTH and 0 <= ty < GRID_HEIGHT:
                tile = grid[ty][tx]
                if tile.building is None:
                    comp_data = COMPONENT_DATA.get(comp["type"], {})
                    color = tuple(comp_data.get("color", (100, 100, 100)))
                    building = Building(comp["type"], color, group_id=group_id)
                    tile.set_occupied(building)

    def save_to_file(self, path):
        if not self.components:
            return

        origin_x, origin_y = self.components[0]["pos"]
        normalized = [
            {
                "type": comp["type"],
                "pos": [comp["pos"][0] - origin_x, comp["pos"][1] - origin_y]
            }
            for comp in self.components
        ]

        data = {
            "name": self.name,
            "components": normalized
        }

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def draw_preview(self, screen, grid_x, grid_y, cam_x, cam_y, zoom, offset_y, grid=None):
        tile_px = TILE_SIZE * zoom

        for comp in self.components:
            cx, cy = comp["pos"]
            tx = grid_x + cx
            ty = grid_y + cy

            px = tx * tile_px - cam_x
            py = ty * tile_px - cam_y + offset_y

            # --- Check tile status
            invalid = False
            if not (0 <= tx < GRID_WIDTH and 0 <= ty < GRID_HEIGHT):
                invalid = True
            elif grid:
                comp_data = COMPONENT_DATA.get(comp["type"], {})
                color = tuple(comp_data.get("color", (100, 100, 100)))
                size = tuple(comp_data.get("size", [1, 1]))
                valid_tile_types = comp_data.get("valid_tile_types", [])
                valid_subtypes = comp_data.get("valid_subtypes", [])
                virtual_comp = Component(comp["type"], color, size, valid_tile_types, valid_subtypes)

                if not grid[ty][tx].is_placeable_by(virtual_comp):
                    invalid = True

            # --- Draw red or green highlight underlay
            tile_highlight = pygame.Surface((tile_px, tile_px), pygame.SRCALPHA)
            tile_highlight.fill((255, 0, 0, 80) if invalid else (0, 255, 0, 60))
            screen.blit(tile_highlight, (int(px), int(py)))

            # --- Draw component ghost
            color = tuple(COMPONENT_DATA.get(comp["type"], {}).get("color", (100, 100, 100)))
            size = tuple(COMPONENT_DATA.get(comp["type"], {}).get("size", [1, 1]))

            width = size[0] * tile_px - int(8 * zoom)
            height = size[1] * tile_px - int(8 * zoom)
            offset = int(4 * zoom)

            surf = pygame.Surface((width, height), pygame.SRCALPHA)
            surf.fill(color + (200,))
            screen.blit(surf, (int(px) + offset, int(py) + offset))

    def rotate_90(self):
        if not self.components:
            return

        max_x = max(comp["pos"][0] for comp in self.components)
        max_y = max(comp["pos"][1] for comp in self.components)

        self.components = [
            {"type": comp["type"], "pos": (max_y - comp["pos"][1], comp["pos"][0])}
            for comp in self.components
        ]

    def flip_horizontal(self):
        if not self.components:
            return

        max_x = max(comp["pos"][0] for comp in self.components)

        for comp in self.components:
            x, y = comp["pos"]
            comp["pos"] = (max_x - x, y)

    def flip_vertical(self):
        if not self.components:
            return

        max_y = max(comp["pos"][1] for comp in self.components)

        for comp in self.components:
            x, y = comp["pos"]
            comp["pos"] = (x, max_y - y)