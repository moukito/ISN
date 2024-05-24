import pygame

from vue.core import Core
from vue.scene import scene


class Pause(scene.Scene):
    def __init__(self, core: Core, parent_render: callable):
        super().__init__(core)

        self.parent_render = parent_render
        self.opacity = pygame.Surface(
            (self.screen.get_width(), self.screen.get_height())
        )
        self.opacity.set_alpha(128)

        self.scale = 0.1

    def handle_events(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False

    def update(self):
        if self.scale < 0.9:
            self.scale += 0.1

    def render(self):
        self.parent_render()
        self.screen.blit(self.opacity, (0, 0))

    def render_pause(self, screen: pygame.Surface):
        pass
