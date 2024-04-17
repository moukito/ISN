import pygame
import threading
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
        """
            Initializes the Scene instance with the screen.

            Parameters:
                screen (pygame.Surface): The surface to render the scene on.
        """
        self.running = False
        self.screen = screen

    def run(self):
        """
            Runs the scene loop.
        """
        self.running = True

        threading.Thread(target=self.event_loop)

        while self.running:
            self.decorator_update()
            self.decorator_render()

    def decorator_handle_events(self):
        """
            Decorator method for handling events.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.handle_events(event)
        pygame.event.clear()

    def decorator_update(self):
        """
            Decorator method for updating the scene.
        """
        self.update()

    def decorator_render(self):
        """
            Decorator method for rendering the scene.
        """
        self.screen.fill((255, 255, 255))

        self.render()

        pygame.display.flip()

    def event_loop(self):
        while self.running:
            self.decorator_handle_events()

    @abstractmethod
    def handle_events(self, event):
        """
            Abstract method for handling events.
            To be implemented in subclasses.
        """
        pass

    @abstractmethod
    def update(self):
        """
            Abstract method for updating the scene.
            To be implemented in subclasses.
        """
        pass

    @abstractmethod
    def render(self):
        """
            Abstract method for rendering the scene.
            To be implemented in subclasses.
        """
        pass
