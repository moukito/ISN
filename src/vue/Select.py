import pygame


class Select:
    def __init__(self, x, y, width, height, options):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.options = options
        self.value = options[0]
        self.is_open = False

    def render(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(self.x, self.y, self.width, self.height))
        text = pygame.font.Font(None, 36).render(str(self.value), 1, (0, 0, 0))
        screen.blit(text, pygame.Rect(self.x, self.y, self.width, self.height).move(5, 5))
        if self.is_open:
            for i, option in enumerate(self.options):
                rect = pygame.Rect(self.x, self.y + (i + 1) * self.height, self.width, self.height)
                pygame.draw.rect(screen, (255, 255, 255), rect)
                text = pygame.font.Font(None, 36).render(str(option), 1, (0, 0, 0))
                screen.blit(text, rect.move(5, 5))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if pygame.Rect(self.x, self.y, self.width, self.height).collidepoint(event.pos):
                self.is_open = not self.is_open
            elif self.is_open:
                for i, option in enumerate(self.options):
                    rect = pygame.Rect(self.x, self.y + (i + 1) * self.height, self.width, self.height)
                    if rect.collidepoint(event.pos):
                        self.value = option
                        self.is_open = False

    def get_value(self):
        return self.value
