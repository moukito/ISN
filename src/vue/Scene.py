import pygame
from abc import ABC, abstractmethod


class Scene(ABC):
    """
        Abstract base class for defining game scenes.
        Provides a template for handling events, updating, and rendering scenes.

        Methods:
            __init__(screen): Initializes the Scene instance with the screen.
            run(): Runs the scene loop.
            decorator_handle_events(): Decorator method for handling events.
            decorator_update(): Decorator method for updating the scene.
            decorator_render(): Decorator method for rendering the scene.
            handle_events(): Abstract method for handling events.
            update(): Abstract method for updating the scene.
            render(): Abstract method for rendering the scene.
    """

    __slots__ = ["running", "screen"]

    def __init__(self, screen: pygame.Surface):
        self.running = False
        self.screen = screen

    def run(self):
        self.running = True
        while self.running:
            self.decorator_handle_events()
            self.decorator_update()
            self.decorator_render()

    def decorator_handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.handle_events()

    def decorator_update(self):
        self.update()

    def decorator_render(self):
        self.screen.fill((255, 255, 255))

        self.render()

        pygame.display.flip()

    @abstractmethod
    def handle_events(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self):
        pass
