import pygame, sys, json
from settings import *
from modes.play_mode import World
from modes.build_mode import BuildGrid
from systems.blueprint import Blueprint
from systems.loaders import load_blueprints
from systems.building import Building
from systems.component import Component
from ui.ui import GUI

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

available_buildings = load_blueprints()
available_components = [
    Component(
        name,
        tuple(data["color"]),
        tuple(data.get("size", (1, 1))),
        data.get("valid_tile_types", []),
        data.get("valid_subtypes", [])
    )
    for name, data in COMPONENT_DATA.items()
]

# --- Game state
gui = GUI()
world = World()
build_grid = BuildGrid()

selected_index = None
build_mode = False
is_panning = False
last_mouse_pos = (0, 0)

try:
    # --- Main loop
    while True:
        dt = clock.tick(FPS)
        screen.fill(BACKGROUND_COLOR)

        target = build_grid if build_mode else world
        target.clear_highlight()
        available_items = available_components if build_mode else available_buildings

        offset_top = gui.top_height
        offset_bottom = gui.bottom_height
        gui_offset = offset_top

        target.update(dt, offset_top=offset_top, offset_bottom=offset_bottom)

        # --- Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                top_bound = gui.top_height
                bottom_bound = SCREEN_HEIGHT - gui.bottom_height

                if event.button == 1:  # Left click
                    index = gui.get_clicked_item_index(mouse_x, mouse_y, available_items)
                    if index is not None:
                        selected_index = index
                    elif top_bound <= mouse_y <= bottom_bound and selected_index is not None:
                        item = available_items[selected_index]
                        target.place_at(mouse_x, mouse_y, offset_y=gui_offset, item=item)

                elif event.button == 3:  # Right click
                    if top_bound <= mouse_y <= bottom_bound:
                        target.remove_at(mouse_x, mouse_y, offset_y=gui_offset)

                elif event.button == 2:  # Middle click for panning
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
                    selected_index = None

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

        # --- Smooth camera motion
        keys = pygame.key.get_pressed()
        target.camera_ax = 0
        target.camera_ay = 0
        if keys[pygame.K_w]: target.camera_ay = -target.scroll_accel
        if keys[pygame.K_s]: target.camera_ay = target.scroll_accel
        if keys[pygame.K_a]: target.camera_ax = -target.scroll_accel
        if keys[pygame.K_d]: target.camera_ax = target.scroll_accel

        # --- Highlight logic
        mouse_x, mouse_y = pygame.mouse.get_pos()
        target.highlight_tile_at(mouse_x, mouse_y, offset_y=gui_offset)

        # --- Draw world / build grid
        target.draw(screen, offset_y=gui_offset)

        # --- Blueprint preview (only in world mode)
        if not build_mode and selected_index is not None:
            selected_item = available_items[selected_index]
            if isinstance(selected_item, Blueprint):
                grid_x, grid_y = target.screen_to_grid(mouse_x, mouse_y, offset_y=gui_offset)

                # Set highlight modes
                for comp in selected_item.components:
                    cx, cy = comp["pos"]
                    tx, ty = grid_x + cx, grid_y + cy
                    if 0 <= tx < GRID_WIDTH and 0 <= ty < GRID_HEIGHT:
                        virtual_tile = world.grid[ty][tx]
                        comp_data = COMPONENT_DATA.get(comp["type"], {})
                        virtual_comp = Component(
                            comp["type"],
                            tuple(comp_data.get("color", (100, 100, 100))),
                            tuple(comp_data.get("size", [1, 1])),
                            comp_data.get("valid_tile_types", []),
                            comp_data.get("valid_subtypes", [])
                        )
                        virtual_tile.highlight_mode = (
                            "buildable" if virtual_tile.is_placeable_by(virtual_comp) else "invalid"
                        )

                selected_item.draw_preview(
                    screen, grid_x, grid_y,
                    cam_x=target.camera_x,
                    cam_y=target.camera_y,
                    zoom=target.zoom,
                    offset_y=gui_offset,
                    grid=world.grid
                )
        
        # --- Preview for build mode (single component)
        elif build_mode and selected_index is not None:
            selected_item = available_items[selected_index]
            if isinstance(selected_item, Component):
                grid_x, grid_y = build_grid.screen_to_grid(mouse_x, mouse_y, offset_y=gui_offset)

                # Component placement bounds
                comp_width, comp_height = selected_item.size
                tile_px = TILE_SIZE * build_grid.zoom
                px = grid_x * tile_px - build_grid.camera_x
                py = grid_y * tile_px - build_grid.camera_y + gui_offset

                # Check validity of all covered tiles
                invalid = False
                for dy in range(comp_height):
                    for dx in range(comp_width):
                        tx, ty = grid_x + dx, grid_y + dy
                        if not (0 <= tx < GRID_WIDTH and 0 <= ty < GRID_HEIGHT):
                            invalid = True
                        elif not build_grid.grid[ty][tx].is_clear():
                            invalid = True

                # --- Highlight
                overlay = pygame.Surface((comp_width * tile_px, comp_height * tile_px), pygame.SRCALPHA)
                overlay.fill((255, 0, 0, 80) if invalid else (0, 255, 0, 60))
                screen.blit(overlay, (int(px), int(py)))

                # --- Ghost component
                surf = pygame.Surface((comp_width * tile_px - int(8 * build_grid.zoom),
                                    comp_height * tile_px - int(8 * build_grid.zoom)), pygame.SRCALPHA)
                surf.fill(selected_item.color + (200,))
                offset = int(4 * build_grid.zoom)
                screen.blit(surf, (int(px) + offset, int(py) + offset))
        
        # --- Basic hover highlight when no preview active
        else:
            target.highlight_tile_at(mouse_x, mouse_y, offset_y=gui_offset)

        # --- Debug overlay
        grid_x, grid_y = target.screen_to_grid(mouse_x, mouse_y, offset_y=gui_offset)
        tile_info = "Out of bounds"
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            tile = target.grid[grid_y][grid_x]
            tile_info = f"{tile.tile_type}"
            if tile.subtype:
                tile_info += f":{tile.subtype}"
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
except Exception as e:
    import traceback
    traceback.print_exc()
    pygame.quit()
    sys.exit()