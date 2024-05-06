import pygame

from src.vue.Scene import Scene


class SettingsScene(Scene):
    """
        Represents the settings screen of the game.
        Inherits from the Scene class.

        Methods:
            __init__(screen): Initializes the SettingsScene instance with the screen.
            handle_events(): Handles events specific to the settings screen.
            update(): Updates the settings screen.
            render(): Renders the settings screen.
            increase_volume(): Increases the game volume.
            decrease_volume(): Decreases the game volume.
            change_resolution(): Changes the game resolution.
    """

    def __init__(self, screen: pygame.Surface):
        """
            Initializes the SettingsScene instance with the screen.

            Parameters:
                screen (pygame.Surface): The surface to render the settings screen on.
        """
        super().__init__(screen)
        self.volume = pygame.mixer.music.get_volume()
        self.resolution = (self.screen.get_width(), self.screen.get_height())
        self.run()

    def handle_events(self, event: pygame.event.Event):
        """
            Handles events specific to the settings screen.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.increase_volume()
            elif event.key == pygame.K_DOWN:
                self.decrease_volume()
            elif event.key == pygame.K_r:
                self.change_resolution()

    def update(self):
        """
            Updates the settings screen.
        """
        pass

    def render(self):
        """
            Renders the settings screen.
        """
        self.screen.fill((0, 0, 0))
        volume_text = pygame.font.Font(None, 36).render(f"Volume: {self.volume}", 1, (255, 255, 255))
        resolution_text = pygame.font.Font(None, 36).render(f"Resolution: {self.resolution}", 1, (255, 255, 255))
        self.screen.blit(volume_text, (20, 20))
        self.screen.blit(resolution_text, (20, 60))

    def increase_volume(self):
        """
            Increases the game volume.
        """
        self.volume = min(1.0, self.volume + 0.1)
        pygame.mixer.music.set_volume(self.volume)

    def decrease_volume(self):
        """
            Decreases the game volume.
        """
        self.volume = max(0.0, self.volume - 0.1)
        pygame.mixer.music.set_volume(self.volume)

    def change_resolution(self):
        """
            Changes the game resolution.
        """
        if self.resolution == (800, 600):
            self.resolution = (1024, 768)
        else:
            self.resolution = (800, 600)
        pygame.display.set_mode(self.resolution)
