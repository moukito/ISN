import pygame


class Button:
    def __init__(self, text, x, y, width, height, color, font=None, font_size=36):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.font = pygame.font.Font(font, font_size)

    def render(self, screen):
        pygame.draw.rect(screen, self.color, pygame.Rect(self.x, self.y, self.width, self.height))
        text = self.font.render(self.text, 1, (255, 255, 255))
        text_width, text_height = text.get_size()
        screen.blit(text, (self.x + self.width // 2 - text_width // 2, self.y + self.height // 2 - text_height // 2.5))

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            return self.x <= mouse_pos[0] <= self.x + self.width and self.y <= mouse_pos[1] <= self.y + self.height
        return False

    def get_size(self):
        return self.width, self.height

    def is_hovered(self, event):
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            return self.x <= mouse_pos[0] <= self.x + self.width and self.y <= mouse_pos[1] <= self.y + self.height
