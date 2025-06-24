from settings import *

class Tile:
    def __init__(self, tile_type="basic", subtype=None):
        self.tile_type = tile_type      # "basic" or "resource"
        self.subtype = subtype          # e.g. "coal", "iron", etc.
        self.state = "clear"            # or "occupied"
        self.building = None
        self.highlight_mode = None      # "buildable", "invalid", etc.
        self.highlighted = False

    def is_clear(self):
        return self.state == "clear" and self.building is None

    def is_buildable(self):
        return self.is_clear()

    def set_occupied(self, obj):
        self.state = "occupied"
        self.building = obj

    def clear(self):
        self.state = "clear"
        self.building = None

    def is_placeable_by(self, component, strict=True):
        """Checks if a component can be placed on this tile"""
        if not self.is_clear():
            return False

        if strict and hasattr(component, "valid_tile_types"):
            if self.tile_type not in component.valid_tile_types:
                return False
            if component.valid_subtypes and self.subtype not in component.valid_subtypes:
                return False

        return True
    
    def clear_highlight(self):
        self.highlight_mode = None
        self.highlighted = False

    def get_color(self):
        if self.building is not None:
            base = TILE_BASE_COLORS.get("building", TILE_BASE_COLORS["building_fallback"])
        else:
            key = f"{self.tile_type}:{self.subtype}" if self.tile_type == "resource" else self.tile_type
            base = TILE_BASE_COLORS.get(key, TILE_BASE_COLORS["unknown"])

        # Prioritize highlight_mode first
        color = HIGHLIGHT_COLORS.get(self.highlight_mode, base)

        # Apply hover highlight
        if self.highlighted:
            return tuple(min(c + 40, 255) for c in color)  # brighten on hover

        return color