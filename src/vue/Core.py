import json
import os
import pickle
import subprocess

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

    __slots__ = ["screen", "title_screen", "parameter"]

    def __init__(self):
        """
            Initializes the Core instance.
        """
        self.screen = None
        self.title_screen = None
        self.parameter = None

        pygame.init()

    def __del__(self):
        """
        Close the game and exit pygame.
        """
        pygame.quit()

    @staticmethod
    def window_setup():
        """
            Initializes the pygame module.
        """
        pygame.display.set_caption("Exodus", "exodus icon")
        pygame.display.set_icon(pygame.image.load("asset/icon/exodus.png"))

    def setup_parameter(self):
        """
            Sets up the game parameters based on configuration.
        """
        self.window_setup()

        if not os.path.isfile("config"):
            self.default_config()

        dico = self.read_config()

        if dico.get("version") != self.game_version():
            self.update_parameter(dico)
            dico = self.read_config()

        if dico["fullscreen"]:
            self.screen = pygame.display.set_mode((dico["width"], dico["height"]), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((dico["width"], dico["height"]))
        self.parameter = dico

    @staticmethod
    def read_config():
        with open("config", "rb") as configFile:
            dico = pickle.load(configFile)
        return dico

    def default_config(self):
        """
            Returns default configuration parameters.
        """
        with open("config", "wb") as configFile:
            pickle.dump(
                dict(version=self.game_version(), fullscreen=True, width=2560,
                     height=1600, volume=0.1), configFile)

    @staticmethod
    def game_version() -> str:
        """
            Returns the version of the game.
        """
        patch = subprocess.run(['git', 'rev-list', '--all', '--count'], capture_output=True).stdout.decode(
            'utf-8').strip()
        return "0.0." + str(patch)

    def update_parameter(self, dico):
        """
            Updates the game parameters if necessary.
        """
        self.default_config()

        default_dico = self.read_config()

        with open("config", "wb") as configFile:
            for key in dico.keys():
                if key != "version":
                    default_dico[key] = dico[key]
            pickle.dump(default_dico, configFile)

    def run(self):
        """
            Starts the game execution.
        """
        self.title_screen = GameTitle(self)
        self.title_screen.setup()
        self.title_screen.run()
        del self.title_screen
