import pygame

from vue.Button import Button
from vue.Scene import Scene
from vue.Select import Select
from vue.Slider import Slider


# TODO : adjust the select and slider class to the new structure
# TODO : make pygame a global import
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

        self.volume_slider = Slider(20, 100, 200, 20, 0.0, 1.0, self.volume)
        self.resolution_menu = Select(20, 200, 200, 50,
                                      [(800, 600), (1024, 768), (1920, 1080), (2560, 1440), (3840, 2160)])

        button_width = self.screen.get_width() * 0.156
        button_height = self.screen.get_height() * 0.062
        font_size = int(self.screen.get_height() * 0.065)

        self.apply_button = Button("Apply", self.screen.get_width() * 3 / 4 - button_width / 2,
                                   self.screen.get_height() * 0.9, button_width, button_height, (0, 255, 0),
                                   "asset/font/Space-Laser-BF65f80ab15c082.otf", font_size)
        self.cancel_button = Button("Cancel", self.screen.get_width() / 4 - button_width / 2,
                                    self.screen.get_height() * 0.9, button_width, button_height, (255, 0, 0),
                                    "asset/font/Space-Laser-BF65f80ab15c082.otf", font_size)

    def handle_events(self, event: pygame.event.Event):
        """
            Handles events specific to the settings screen.
        """
        if self.apply_button.is_clicked(event):
            # Apply the settings
            pygame.mixer.music.set_volume(self.volume)
            pygame.display.set_mode(self.resolution)

            self.parameter["volume"] = self.volume
            self.parameter["width"] = self.resolution[0]
            self.parameter["height"] = self.resolution[1]

            self.core.update_parameter(self.parameter)

            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif self.cancel_button.is_clicked(event):
            # Cancel the settings
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        elif event.type == pygame.MOUSEMOTION:
            for button in [self.apply_button, self.cancel_button]:
                if button.is_hovered(event):
                    self.change_button_color(button, True)
                else:
                    self.change_button_color(button, False)
        self.volume_slider.handle_event(event)
        self.resolution_menu.handle_event(event)

    def update(self):
        """
            Updates the settings screen.
        """
        self.volume = self.volume_slider.get_value()
        self.resolution = self.resolution_menu.get_value()

    def render(self):
        """
            Renders the settings screen.
        """
        volume_text = pygame.font.Font(None, 36).render(f"Volume: {self.volume}", 1, (255, 255, 255))
        self.volume_slider.render(self.screen)

        resolution_text = pygame.font.Font(None, 36).render(f"Resolution: {self.resolution}", 1, (255, 255, 255))
        self.resolution_menu.render(self.screen)

        self.screen.blit(volume_text, (20, 20))
        self.screen.blit(resolution_text, (20, 60))

        self.apply_button.render(self.screen)
        self.cancel_button.render(self.screen)

    @staticmethod
    def change_button_color(button, hovered):
        """
            Changes the color of the button when hovered.

            Parameters:
                button (Button): The button to change the color of.
                hovered (bool): Whether the button is hovered or not.
        """
        if hovered:
            if button.text == "Apply":
                button.color = (0, 255, 0)
            else:
                button.color = (255, 0, 0)
        else:
            if button.text == "Apply":
                button.color = (0, 200, 0)
            else:
                button.color = (200, 0, 0)
