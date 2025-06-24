import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

TOP_UI_PADDING = 5
UI_BOTTOM_HEIGHT = 120  # Height of the bottom UI panel

class GUI:

    def __init__(self, font_size=16):
        self.font = pygame.font.SysFont("consolas", font_size)
        self.bg_color = (30, 30, 30)
        self.text_color = (255, 255, 255)
        self.padding = 5
        self.line_height = font_size + 4
        self.padding = TOP_UI_PADDING


        self.top_height = 0          # Updated in draw()
        self.bottom_height = UI_BOTTOM_HEIGHT

    def draw(self, screen, debug_lines=None, items=None, selected_index=None):
        # --- Top UI bar (e.g. debug)
        self.top_height = len(debug_lines) * self.line_height + 2 * self.padding if debug_lines else 0
        pygame.draw.rect(screen, self.bg_color, (0, 0, SCREEN_WIDTH, self.top_height))

        if debug_lines:
            for i, line in enumerate(debug_lines):
                text_surf = self.font.render(line, True, self.text_color)
                screen.blit(text_surf, (self.padding, self.padding + i * self.line_height))

        # --- Bottom UI bar (e.g. items)
        ui_rect = pygame.Rect(0, SCREEN_HEIGHT - self.bottom_height, SCREEN_WIDTH, self.bottom_height)
        pygame.draw.rect(screen, (40, 40, 40), ui_rect)

        if items:
            self.draw_item_buttons(screen, items, selected_index)

    def draw_item_buttons(self, screen, items, selected_index):
        button_width = 100
        button_height = 80
        padding = 10
        y = SCREEN_HEIGHT - self.bottom_height + 20

        for i, item in enumerate(items):
            x = padding + i * (button_width + padding)
            rect = pygame.Rect(x, y, button_width, button_height)

            if i == selected_index:
                # Highlight background
                pygame.draw.rect(screen, (80, 80, 120), rect)

            # Main button color
            color = (70, 70, 70)
            pygame.draw.rect(screen, color, rect)

            # Draw border
            border_color = (255, 255, 0) if i == selected_index else (200, 200, 200)
            pygame.draw.rect(screen, border_color, rect, 2)

            # Label
            label = self.font.render(item.name, True, self.text_color)
            label_rect = label.get_rect(center=rect.center)
            screen.blit(label, label_rect)

    def get_clicked_item_index(self, mouse_x, mouse_y, items):
        button_width = 100
        button_height = 80
        padding = 10
        y = SCREEN_HEIGHT - self.bottom_height + 20

        for i, item in enumerate(items):
            x = padding + i * (button_width + padding)
            rect = pygame.Rect(x, y, button_width, button_height)
            if rect.collidepoint(mouse_x, mouse_y):
                return i
        return None

class BlueprintNamingOverlay:
    def __init__(self, font, x, y, width):
        self.font = font
        self.rect = pygame.Rect(x, y, width, 40)
        self.active = False
        self.text = ""
        self.cursor_visible = True
        self.cursor_timer = 0

    def open(self):
        self.active = True
        self.text = ""

    def close(self):
        self.active = False

    def handle_event(self, event):
        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                name = self.text.strip()
                self.close()
                return name
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isprintable():
                self.text += event.unicode

        return None

    def update(self, dt):
        if self.active:
            self.cursor_timer += dt
            if self.cursor_timer > 500:
                self.cursor_timer = 0
                self.cursor_visible = not self.cursor_visible

    def draw(self, screen):
        if not self.active:
            return

        pygame.draw.rect(screen, (30, 30, 30), self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)

        text_surf = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(text_surf, (self.rect.x + 5, self.rect.y + 8))

        # Draw blinking cursor
        if self.cursor_visible:
            cursor_x = self.rect.x + 5 + text_surf.get_width() + 2
            cursor_y = self.rect.y + 8
            pygame.draw.line(screen, (255, 255, 255), (cursor_x, cursor_y), (cursor_x, cursor_y + 24), 2)
