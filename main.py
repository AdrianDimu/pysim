import pygame, sys
from config import *
from core.world import World
from core.buildgrid import BuildGrid
from core.machine import Machine
from core.gui import GUI

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("pysim")
clock = pygame.time.Clock()

available_items = [
    Machine("TST", (150, 200, 255)),
    Machine("TST2", (255, 180, 80))
]
selected_item_index = 0  # Default to TST

gui = GUI()
world = World()
build_grid = BuildGrid()

selected_index = None
build_mode = False
is_panning = False
last_mouse_pos = (0, 0)

while True:
    dt = clock.tick(FPS)
    screen.fill(BACKGROUND_COLOR)

    target = build_grid if build_mode else world

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
            top_bound = gui.top_height
            bottom_bound = SCREEN_HEIGHT - gui.bottom_height

            if event.button == 1:
                # Left click
                index = gui.get_clicked_item_index(mouse_x, mouse_y, available_items)
                if index is not None:
                    selected_index = index
                elif top_bound <= mouse_y <= bottom_bound and selected_index is not None:
                    if 0 <= selected_index < len(available_items):
                        item = available_items[selected_index]
                        target.place_at(mouse_x, mouse_y, offset_y=gui_offset, item=item)

            elif event.button == 3:
                # Right click to remove
                if top_bound <= mouse_y <= bottom_bound:
                    target.remove_at(mouse_x, mouse_y, offset_y=gui_offset)
                                    
            elif event.button == 2:
                # Middle click for panning
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
            if event.key == pygame.K_b:
                build_mode = not build_mode
                print("Build mode ON" if build_mode else "World mode ON")

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

    # --- Draw world/buildgrid
    target.draw(screen, offset_y=gui_offset)

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
    gui.draw(screen, debug_lines, items=available_items if not build_mode else None, selected_index=selected_index if not build_mode else None)

    pygame.display.flip()