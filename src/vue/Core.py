import json
import os

import pygame

from src.vue.GameTitle import GameTitle


class Core:
    """
        Represents the core of the game.
        Handles game initialization, configuration, and execution.

        Methods:
            __init__(): Initializes the Core instance.
            __del__(): Closes the game and exits pygame.
            setup_parameter(): Sets up the game parameters based on configuration.
            default_config() -> dict: Returns default configuration parameters.
            game_version(): Returns the version of the game.
            update_parameter(): Updates the game parameters if necessary.
            run(): Starts the game execution.
    """

    __slots__ = ["screen", "title_screen"]

    def __init__(self):
        """
            Initializes the Core instance.
        """
        pygame.init()
        self.screen = None
        self.title_screen = None

        pygame.display.set_caption("Exodus", "exodus icon")
        pygame.display.set_icon(pygame.image.load("asset/icon/exodus.png"))

        self.setup_parameter()

    def __del__(self):
        """
        Close the game and exit pygame.
        """
        pygame.quit()

    def setup_parameter(self):
        """
            Sets up the game parameters based on configuration.
        """
        if not os.path.isfile("config.json"):
            with open("config.json", "w") as configFile:
                json.dump(self.default_config(), configFile)

        with open("config.json", "r") as configFile:
            dico = json.load(configFile)
            if dico.get("version") != self.game_version():
                self.update_parameter()

        if dico["fullscreen"]:
            self.screen = pygame.display.set_mode((dico["width"], dico["height"]), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((dico["width"], dico["height"]))

    def default_config(self) -> dict:
        """
            Returns default configuration parameters.
        """
        return dict(version="1.0.0", fullscreen=True, width=pygame.display.get_desktop_sizes()[0][0],
                    height=pygame.display.get_desktop_sizes()[0][1])

    def game_version(self) -> str:
        """
            Returns the version of the game.
        """
        return "1.0.0"

    def update_parameter(self):
        """
            Updates the game parameters if necessary.
        """
        pass

    def run(self):
        """
            Starts the game execution.
        """
        self.title_screen = GameTitle(self.screen)
