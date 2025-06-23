from config import *

class Tile:
    def __init__(self, type_name):
        self.type = type_name
        self.building = None  # Later we'll store a machine here
        self.highlighted = False

    def is_buildable(self):
        return self.type in {"clear"}

    def get_color(self):
        base = TILE_TYPES.get(self.type, (100, 100, 100))
        if self.highlighted:
            return tuple(min(c + 40, 255) for c in base)
        return base