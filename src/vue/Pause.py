import pygame
import sys
import json

from vue.Button import Button
from vue.Scene import Scene
from vue.Select import Select
from vue.Slider import Slider
from vue.SettingScene import SettingsScene
from vue.SavesScene import SavesScene
from vue.GameTitle import GameTitle



class Pause(Scene):
    """
    Represents the pause screen of the game.
    Inherits from the Scene class.

    Methods:
        __init__(screen): Initializes the Pause scene instance with the screen.
        handle_events(): Handles events specific to the settings screen.
        update(): Updates the settings screen.
        render(): Renders the settings screen.
    """

    def __init__(self, core, parent_render):
        """
        Initializes the PauseScene instance with the screen.

        Parameters:
            core (pygame.Surface): The surface to render the pause screen on.
        """
        super().__init__(core)
        self.parent_render = parent_render
        self.opacity = pygame.Surface(
            (self.screen.get_width(), self.screen.get_height())
        )
        self.opacity.set_alpha(160)
        self.scale = 0.0

        self.volume = pygame.mixer.music.get_volume()
        self.resolution = (self.screen.get_width(), self.screen.get_height())

        self.volume_slider = Slider(20, 100, 200, 20, 0.0, 1.0, self.volume)
        self.resolution_menu = Select(
            20,
            200,
            200,
            50,
            [(800, 600), (1024, 768), (1920, 1080), (2560, 1440), (3840, 2160)],
            self.resolution,
        )

        button_width = self.screen.get_width() * 0.156
        button_height = self.screen.get_height() * 0.062
        font_size = int(self.screen.get_height() * 0.065)

        self.reprendre_button = Button(
            "Reprendre",
            self.screen.get_width() * 3 / 4  - button_width / 2,
            self.screen.get_height() * 0.9,
            self.screen.get_width() * 0.200,
            button_height,
            (0, 255, 0),
            "assets/font/Space-Laser-BF65f80ab15c082.otf",
            font_size,
        )
        self.quitter_button = Button(
            "Quitter",
            self.screen.get_width() / 4 - button_width / 2,
            self.screen.get_height() * 0.9,
            button_width,
            button_height,
            (255, 0, 0),
            "assets/font/Space-Laser-BF65f80ab15c082.otf",
            font_size,
        )
        self.save_button = Button(
            "Sauvegarder",
            self.screen.get_width() * 11 / 24 - button_width / 2,
            self.screen.get_height() * 0.4,
            self.screen.get_width() * 0.250,
            button_height,
            (0, 0, 255),
            "assets/font/Space-Laser-BF65f80ab15c082.otf",
            font_size,
        )
        self.settings_button = Button(
            "Options",
            self.screen.get_width() * 11 / 24 - button_width / 2,
            self.screen.get_height() * 0.6,
            self.screen.get_width() * 0.250,
            button_height,
            (0, 0, 255),
            "assets/font/Space-Laser-BF65f80ab15c082.otf",
            font_size,
        )

    def handle_events(self, event: pygame.event.Event):
        """
        Handles events specific to the pause screen.
        """
        if self.reprendre_button.is_clicked(event):
            pygame.event.post(pygame.event.Event(self.event, {"scene": "title"}))
            self.running = False
        elif self.quitter_button.is_clicked(event):
            pygame.event.post(pygame.event.Event(self.event, {"scene": "quit"}))
            pygame.quit()
            sys.exit()
        elif self.save_button.is_clicked(event) :
            saves_scene = SavesScene(
                self.core, self.render
            )  # Create and run the saves scene
            saves_scene.run()
        elif self.settings_button.is_clicked(event) :
            settings_scene = SettingsScene(
                self.core, self.render
            )  # Create and run the settings scene
            settings_scene.run()
        elif event.type == pygame.MOUSEMOTION:
            for button in [self.reprendre_button, self.quitter_button, self.save_button, self.settings_button]:
                if button.is_hovered(event):
                    self.change_button_color(button, True)
                else:
                    self.change_button_color(button, False)
        self.volume_slider.handle_event(event)
        self.resolution_menu.handle_event(event)

    def update(self):
        """
        Updates the pause screen.
        """
        self.volume = self.volume_slider.get_value()
        pygame.mixer.music.set_volume(self.volume)

        self.resolution = self.resolution_menu.get_value()

        if self.scale < 0.99:
            self.scale += 0.02
    
    def update_parameter(self, dico):
        """
        Updates the game parameters if necessary.
        """
        self.default_config()

        default_dico = self.read_config()

        with open("config.json", "w") as configFile:
            for key in dico.keys():
                if key != "version":
                    default_dico[key] = dico[key]
            json.dump(default_dico, configFile)

    def update_screen(self):
        if self.parameter["fullscreen"]:
            flags = pygame.FULLSCREEN | pygame.SCALED
        else:
            flags = pygame.SCALED
        self.screen = pygame.display.set_mode(
            (self.parameter["width"], self.parameter["height"]), flags
        )

    def render(self):
        """
        Renders the pause screen.
        """
        self.parent_render()

        self.screen.blit(self.opacity, (0, 0))

        self.reprendre_button.render(self.screen)
        self.quitter_button.render(self.screen)
        self.save_button.render(self.screen)
        self.settings_button.render(self.screen)

    @staticmethod
    def change_button_color(button, hovered):
        """
        Changes the color of the button when hovered.

        Parameters:
            button (Button): The button to change the color of.
            hovered (bool): Whether the button is hovered or not.
        """
        if hovered:
            if button.text == "Reprendre":
                button.color = (0, 255, 0)
            elif button.text == "Quitter":
                button.color = (255, 0, 0)
            else :
                button.color = (0, 0, 255)
        else:
            if button.text == "Reprendre":
                button.color = (0, 200, 0)
            elif button.text == "Quitter":
                button.color = (200, 0, 0)
            else : 
                button.color = (0, 0, 200)