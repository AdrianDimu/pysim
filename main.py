import pygame, sys
from config import *
from core.world import World
from core.gui import GUI

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("pysim")
clock = pygame.time.Clock()

gui = GUI()
world = World()

is_panning = False
last_mouse_pos = (0, 0)

while True:
    dt = clock.tick(FPS)
    screen.fill(BACKGROUND_COLOR)

    world.update(dt)
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                world.place_machine_at(*pygame.mouse.get_pos(), offset_y=gui.last_height)
            elif event.button == 2:
                is_panning = True
                last_mouse_pos = pygame.mouse.get_pos()
            elif event.button == 4 or event.button == 5:
                delta = 1 if event.button == 4 else -1
                mouse_x, mouse_y = pygame.mouse.get_pos()
                world.adjust_zoom(delta, mouse_x, mouse_y, offset_y=gui.last_height)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                is_panning = False
        
        elif event.type == pygame.MOUSEMOTION and is_panning:
            mx, my = pygame.mouse.get_pos()
            dx = last_mouse_pos[0] - mx
            dy = last_mouse_pos[1] - my
            world.camera_x += dx
            world.camera_y += dy
            world.clamp_camera()
            last_mouse_pos = (mx, my)

        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world.adjust_zoom(event.y * 0.1, mouse_x, mouse_y, offset_y=gui.last_height)

    # Smooth camera acceleration based on key state
    keys = pygame.key.get_pressed()

    world.camera_ax = 0
    world.camera_ay = 0

    if keys[pygame.K_w]: world.camera_ay = -world.scroll_accel
    if keys[pygame.K_s]: world.camera_ay = world.scroll_accel
    if keys[pygame.K_a]: world.camera_ax = -world.scroll_accel
    if keys[pygame.K_d]: world.camera_ax = world.scroll_accel

    # Mouse highlight
    mouse_x, mouse_y = pygame.mouse.get_pos()
    world.clear_highlight()
    world.highlight_tile_at(mouse_x, mouse_y, offset_y=gui.last_height)

    # Draw world
    world.draw(screen, offset_y=gui.last_height)

    # Debug Info Overlay
    grid_x, grid_y = world.screen_to_grid(mouse_x, mouse_y, offset_y=gui.last_height)

    tile_info = ""
    if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
        tile = world.grid[grid_y][grid_x]
        tile_info = f"{tile.type}"
        if tile.building:
            tile_info += f" | {tile.building.name}"

    debug_lines = [
        f"Zoom: {world.zoom:.2f}",
        f"Mouse Screen: ({mouse_x}, {mouse_y})",
        f"Mouse Grid: ({grid_x}, {grid_y})",
        f"Tile: {tile_info}",
        f"Camera: ({int(world.camera_x)}, {int(world.camera_y)})"
    ]

    gui.draw(screen, debug_lines)

    pygame.display.flip()