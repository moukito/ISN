import pygame


class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.dragging = False

    def render(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(self.x, self.y, self.width, self.height))
        handle_x = self.x + (self.value - self.min_val) / (self.max_val - self.min_val) * self.width
        pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(handle_x - 5, self.y, 10, self.height))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.x <= event.pos[0] <= self.x + self.width and self.y <= event.pos[1] <= self.y + self.height:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.value = (event.pos[0] - self.x) / self.width * (self.max_val - self.min_val) + self.min_val
            self.value = max(min(self.value, self.max_val), self.min_val)

    def get_value(self):
        return self.value
