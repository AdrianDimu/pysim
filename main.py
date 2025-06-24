import pygame, sys, json
from config import *
from core.world import World
from core.buildgrid import BuildGrid
from core.blueprint import Blueprint
from core.blueprint_loader import load_blueprints
from core.building import Building
from core.component import Component
from core.gui import GUI

# --- Init
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("pysim")
clock = pygame.time.Clock()

# --- Load data
with open("data/buildings.json") as f:
    BUILDING_DATA = json.load(f)

with open("data/components.json") as f:
    COMPONENT_DATA = json.load(f)

available_buildings = load_blueprints()  # These are blueprints now
available_components = [
    Component(name, tuple(data["color"]), tuple(data["size"])) for name, data in COMPONENT_DATA.items()
]

# --- Game state
gui = GUI()
world = World()
build_grid = BuildGrid()

selected_index = None
build_mode = False
is_panning = False
last_mouse_pos = (0, 0)

# --- Main loop
while True:
    dt = clock.tick(FPS)
    screen.fill(BACKGROUND_COLOR)

    target = build_grid if build_mode else world
    available_items = available_components if build_mode else available_buildings

    # --- Offset calculations
    offset_top = gui.top_height
    offset_bottom = gui.bottom_height
    gui_offset = offset_top

    # --- Update
    target.update(dt, offset_top=offset_top, offset_bottom=offset_bottom)
    
    # --- Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            top_bound = gui.top_height
            bottom_bound = SCREEN_HEIGHT - gui.bottom_height

            if event.button == 1: # Left click
                index = gui.get_clicked_item_index(mouse_x, mouse_y, available_items)
                if index is not None:
                    selected_index = index
                elif top_bound <= mouse_y <= bottom_bound and selected_index is not None:
                    item = available_items[selected_index]
                    target.place_at(mouse_x, mouse_y, offset_y=gui_offset, item=item)

            elif event.button == 3: # Right click to remove
                if top_bound <= mouse_y <= bottom_bound:
                    target.remove_at(mouse_x, mouse_y, offset_y=gui_offset)
                                    
            elif event.button == 2: # Middle click for panning
                is_panning = True
                last_mouse_pos = pygame.mouse.get_pos()

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                is_panning = False

        elif event.type == pygame.MOUSEMOTION and is_panning:
            mx, my = pygame.mouse.get_pos()
            dx = last_mouse_pos[0] - mx
            dy = last_mouse_pos[1] - my
            target.camera_x += dx
            target.camera_y += dy
            target.clamp_camera(offset_top=offset_top, offset_bottom=offset_bottom)
            last_mouse_pos = (mx, my)

        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            delta = event.y * 0.5
            target.adjust_zoom(delta, mouse_x, mouse_y, offset_top=offset_top, offset_bottom=offset_bottom)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                selected_index = None
                print("Selection cleared")

            elif event.key == pygame.K_b:
                build_mode = not build_mode
                print("Build mode ON" if build_mode else "World mode ON")
                selected_index = None # reset selection when switching mode
        
            elif event.key == pygame.K_q and build_mode:

                components = build_grid.extract_blueprint_components()
                if components:
                    blueprint = Blueprint("DrillRig", components)
                    blueprint.save_to_file("data/blueprints/DrillRig.json")
                    print("Blueprint saved as DrillRig.json")

            elif event.key == pygame.K_r and not build_mode and selected_index is not None:
                selected_item = available_items[selected_index]
                if isinstance(selected_item, Blueprint):
                    selected_item.rotate_90()
                    print(f"Rotated blueprint '{selected_item.name}' 90°")
            
            elif event.key == pygame.K_h and not build_mode and selected_index is not None:
                selected_item = available_items[selected_index]
                if isinstance(selected_item, Blueprint):
                    selected_item.flip_horizontal()
                    print(f"Flipped blueprint '{selected_item.name}' horizontally")

            elif event.key == pygame.K_v and not build_mode and selected_index is not None:
                selected_item = available_items[selected_index]
                if isinstance(selected_item, Blueprint):
                    selected_item.flip_vertical()
                    print(f"Flipped blueprint '{selected_item.name}' vertically")

    ## --- Smooth camera motion
    keys = pygame.key.get_pressed()
    target.camera_ax = 0
    target.camera_ay = 0
    if keys[pygame.K_w]: target.camera_ay = -target.scroll_accel
    if keys[pygame.K_s]: target.camera_ay = target.scroll_accel
    if keys[pygame.K_a]: target.camera_ax = -target.scroll_accel
    if keys[pygame.K_d]: target.camera_ax = target.scroll_accel

    # --- Highlight
    mouse_x, mouse_y = pygame.mouse.get_pos()
    target.clear_highlight()
    target.highlight_tile_at(mouse_x, mouse_y, offset_y=gui_offset)

    # Reset highlights before marking new ones
    target.clear_highlight()

    # --- Draw world/buildgrid
    target.draw(screen, offset_y=gui_offset)
    if not build_mode and selected_index is not None:
        selected_item = available_items[selected_index]
        if isinstance(selected_item, Blueprint):
            grid_x, grid_y = target.screen_to_grid(mouse_x, mouse_y, offset_y=gui_offset)

            # Mark highlight mode per tile
            for comp in selected_item.components:
                cx, cy = comp["pos"]
                tx, ty = grid_x + cx, grid_y + cy
                if 0 <= tx < GRID_WIDTH and 0 <= ty < GRID_HEIGHT:
                    tile = world.grid[ty][tx]
                    tile.highlight_mode = (
                    "buildable" if tile.is_buildable() else "invalid"
                    )

            # Draw preview on top
            selected_item.draw_preview(
                screen, grid_x, grid_y,
                cam_x=target.camera_x,
                cam_y=target.camera_y,
                zoom=target.zoom,
                offset_y=gui_offset,
                grid=world.grid
            )

    # --- Debug
    grid_x, grid_y = target.screen_to_grid(mouse_x, mouse_y, offset_y=gui_offset)
    tile_info = "Out of bounds"
    if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
        tile = target.grid[grid_y][grid_x]
        tile_info = f"{tile.type}"
        if tile.building:
            tile_info += f" | {tile.building.name}"

    debug_lines = [
        f"Mode: {'BUILD' if build_mode else 'WORLD'}",
        f"Zoom: {target.zoom:.2f}",
        f"Mouse Screen: ({mouse_x}, {mouse_y})",
        f"Mouse Grid: ({grid_x}, {grid_y})",
        f"Tile: {tile_info}",
        f"Camera: ({int(target.camera_x)}, {int(target.camera_y)})"
    ]

    # --- GUI
    gui.draw(
        screen, 
        debug_lines, 
        items=available_items,
        selected_index=selected_index
    )

    pygame.display.flip()