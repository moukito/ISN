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

    __slots__ = ["running", "screen", "parameter", "core", "event"]

    def __init__(self, core) -> None:
        """
        Initializes the Scene instance with the screen.

        Parameters:
            screen (pygame.Surface): The surface to render the scene on.
        """
        self.running = False
        self.core = core
        self.screen = core.screen
        self.parameter = core.parameter
        self.event = self.core.event

    def run(self) -> None:
        """
        Runs the scene loop.
        """
        self.running = True
        while self.running:
            self.decorator_handle_events()
            self.decorator_update()
            self.decorator_render()

    def decorator_handle_events(self) -> None:
        """
        Decorator method for handling events.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.handle_events(event)

    def decorator_update(self) -> None:
        """
        Decorator method for updating the scene.
        """
        self.update()

    def decorator_render(self) -> None:
        """
        Decorator method for rendering the scene.
        """
        self.render()

        pygame.display.flip()

    @abstractmethod
    def handle_events(self, event: pygame.event.Event) -> None:
        """
        Abstract method for handling events.
        To be implemented in subclasses.
        """
        pass

    @abstractmethod
    def update(self) -> None:
        """
        Abstract method for updating the scene.
        To be implemented in subclasses.
        """
        pass

    @abstractmethod
    def render(self) -> None:
        """
        Abstract method for rendering the scene.
        To be implemented in subclasses.
        """
        pass
