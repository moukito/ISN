import pygame

from src.vue.Scene import Scene


class GameTitle(Scene):
    """
        Represents the title screen of the game.
        Inherits from the Scene class.

        Methods:
            __init__(screen): Initializes the GameTitle instance with the screen.
            handle_events(): Handles events specific to the title screen.
            update(): Updates the title screen.
            render(): Renders the title screen.
    """

    __slots__ = ["bg"]

    def __init__(self, screen: pygame.Surface):
        """
            Initializes the GameTitle instance with the screen.

            Parameters:
                screen (pygame.Surface): The surface to render the title screen on.
        """
        super().__init__(screen)
        self.bg = pygame.image.load("assets/background.jpg")

        self.run()

    def handle_events(self):
        """
            Handles events specific to the title screen.
        """
        pass

    def update(self):
        """
            Updates the title screen.
        """
        pass

    def render(self):
        """
            Renders the title screen.
        """
        self.screen.blit(self.bg, (0, 0))
