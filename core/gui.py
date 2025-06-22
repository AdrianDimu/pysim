import pygame
from config import SCREEN_WIDTH

class GUI:
    def __init__(self, font_size=16):
        self.font = pygame.font.SysFont("consolas", font_size)
        self.bg_color = (30, 30, 30)
        self.text_color = (255, 255, 255)
        self.padding = 5
        self.line_height = font_size + 4

        self.last_height = 0

    def draw(self, screen, debug_lines):
        bar_height = len(debug_lines) * self.line_height + 2 * self.padding
        self.last_height = bar_height  # Save for world offset

        pygame.draw.rect(screen, self.bg_color, (0, 0, SCREEN_WIDTH, bar_height))

        for i, line in enumerate(debug_lines):
            text_surf = self.font.render(line, True, self.text_color)
            screen.blit(text_surf, (self.padding, self.padding + i * self.line_height))