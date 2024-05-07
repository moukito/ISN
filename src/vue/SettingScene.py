import pygame

from src.vue.Button import Button
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

    def __init__(self, core):
        """
            Initializes the SettingsScene instance with the screen.

            Parameters:
                core (pygame.Surface): The surface to render the settings screen on.
        """
        super().__init__(core)
        self.volume = pygame.mixer.music.get_volume()
        self.resolution = (self.screen.get_width(), self.screen.get_height())

        self.apply_button = Button("Apply", 20, self.screen.get_height() - 70, 100, 50, (0, 255, 0))
        self.cancel_button = Button("Cancel", 130, self.screen.get_height() - 70, 100, 50, (255, 0, 0))

        self.run()

    def handle_events(self, event: pygame.event.Event):
        """
            Handles events specific to the settings screen.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            if event.key == pygame.K_UP:
                self.increase_volume()
            elif event.key == pygame.K_DOWN:
                self.decrease_volume()
            elif event.key == pygame.K_r:
                self.change_resolution()
        if self.apply_button.is_clicked(event):
            # Apply the settings
            pygame.mixer.music.set_volume(self.volume)
            pygame.display.set_mode(self.resolution)

            self.parameter["volume"] = self.volume
            self.parameter["width"] = self.resolution[0]
            self.parameter["height"] = self.resolution[1]

        elif self.cancel_button.is_clicked(event):
            # Cancel the settings
            pass
#TODO : create a special event for button

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

        self.apply_button.render(self.screen)
        self.cancel_button.render(self.screen)

    def increase_volume(self):
        """
            Increases the game volume.
        """
        self.volume = min(1.0, self.volume + 0.1)

    def decrease_volume(self):
        """
            Decreases the game volume.
        """
        self.volume = max(0.0, self.volume - 0.1)

    def change_resolution(self):
        """
            Changes the game resolution.
        """
        if self.resolution == (800, 600):
            self.resolution = (1024, 768)
        else:
            self.resolution = (800, 600)
