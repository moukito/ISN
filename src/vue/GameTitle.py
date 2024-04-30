import pygame

from src.vue.Choix import Choix
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

    __slots__ = ["bg", "choix"]

    def __init__(self, screen: pygame.Surface):
        """
            Initializes the GameTitle instance with the screen.

            Parameters:
                screen (pygame.Surface): The surface to render the title screen on.
        """
        super().__init__(screen)
        self.bg = pygame.transform.smoothscale(pygame.image.load("asset/background.jpg"),
                                               (self.screen.get_width(), self.screen.get_height()))
        pygame.mixer.music.load("asset/music/titleScreen.mp3")
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play()

        self.choix = Choix()

        self.run()

    def __del__(self):
        pygame.mixer.music.stop()

    def handle_events(self, event: pygame.event.Event):
        """
            Handles events specific to the title screen.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.key == pygame.K_UP:
                self.choix -= 1
            elif event.key == pygame.K_DOWN:
                self.choix += 1
            elif event.key == pygame.K_RETURN:
                choix = self.choix.get_choix()
                if choix == 1:
                    pass
                elif choix == 2:
                    pass
                elif choix == 3:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

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
