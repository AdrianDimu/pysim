SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 920
TILE_SIZE = 32

# Grid is now independent of screen size
GRID_WIDTH = 100
GRID_HEIGHT = 100

FPS = 60

BLUEPRINT_BG = (230, 240, 255)
BACKGROUND_COLOR = (230, 240, 255)

# Core tile visuals by type/subtype
TILE_BASE_COLORS = {
    "basic": (130, 200, 250),
    "resource:iron": (130, 130, 130),
    "resource:coal": (30, 30, 30),
    "resource:limestone": (200, 200, 120),
    "building": (255, 255, 150),

    # Fallbacks
    "unknown": (100, 100, 100),
    "building_fallback": (255, 255, 150),
}

# Highlight modes
HIGHLIGHT_COLORS = {
    "buildable": (180, 255, 180),
    "invalid": (255, 150, 150),
}