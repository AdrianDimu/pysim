import pygame, sys
from config import *
from core.world import World
from core.buildgrid import BuildGrid
from core.gui import GUI

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("pysim")
clock = pygame.time.Clock()

gui = GUI()
world = World()
build_grid = BuildGrid()

build_mode = False

is_panning = False
last_mouse_pos = (0, 0)

while True:
    dt = clock.tick(FPS)
    screen.fill(BACKGROUND_COLOR)

    # Update
    if build_mode:
        build_grid.update(dt)
    else:
        world.update(dt)
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if build_mode:
                    build_grid.place_machine_at(*pygame.mouse.get_pos())
                else:
                    world.place_machine_at(*pygame.mouse.get_pos(), offset_y=gui.last_height)
            elif event.button == 2:
                is_panning = True
                last_mouse_pos = pygame.mouse.get_pos()

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                is_panning = False
        
        elif event.type == pygame.MOUSEMOTION and is_panning:
            mx, my = pygame.mouse.get_pos()
            dx = last_mouse_pos[0] - mx
            dy = last_mouse_pos[1] - my
            if build_mode:
                build_grid.camera_x += dx
                build_grid.camera_y += dy
                build_grid.clamp_camera()
            else:
                world.camera_x += dx
                world.camera_y += dy
                world.clamp_camera()
            last_mouse_pos = (mx, my)

        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            delta = event.y * 0.5
            if build_mode:
                build_grid.adjust_zoom(delta, mouse_x, mouse_y)
            else:
                world.adjust_zoom(delta, mouse_x, mouse_y, offset_y=gui.last_height)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b:
                build_mode = not build_mode
                print("Build mode ON" if build_mode else "World mode ON")


    # Smooth camera acceleration based on key state
    keys = pygame.key.get_pressed()

    target = build_grid if build_mode else world
    target.camera_ax = 0
    target.camera_ay = 0

    if keys[pygame.K_w]: target.camera_ay = -target.scroll_accel
    if keys[pygame.K_s]: target.camera_ay = target.scroll_accel
    if keys[pygame.K_a]: target.camera_ax = -target.scroll_accel
    if keys[pygame.K_d]: target.camera_ax = target.scroll_accel

    # Mouse highlight
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if build_mode:
        build_grid.clear_highlight()
        build_grid.highlight_tile_at(mouse_x, mouse_y)
    else:
        world.clear_highlight()
        world.highlight_tile_at(mouse_x, mouse_y, offset_y=gui.last_height)

    # Draw world
    if build_mode:
        build_grid.draw(screen)
    else:
        world.draw(screen, offset_y=gui.last_height)

    # Debug Info Overlay
    if build_mode:
        grid_x, grid_y = build_grid.screen_to_grid(mouse_x, mouse_y)
        tile = build_grid.grid[grid_y][grid_x]
    else:
        grid_x, grid_y = world.screen_to_grid(mouse_x, mouse_y, offset_y=gui.last_height)
        tile = world.grid[grid_y][grid_x]

    tile_info = f"{tile.type}"
    if tile.building:
        tile_info += f" | {tile.building.name}"

    debug_lines = [
        f"Mode: {'BUILD' if build_mode else 'WORLD'}",
        f"Zoom: {target.zoom:.2f}",
        f"Mouse Screen: ({mouse_x}, {mouse_y})",
        f"Mouse Grid: ({grid_x}, {grid_y})",
        f"Tile: {tile_info}",
        f"Camera: ({int(world.camera_x)}, {int(world.camera_y)})"
    ]
    gui.draw(screen, debug_lines)

    pygame.display.flip()