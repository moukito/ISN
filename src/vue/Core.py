import json
import os
import pickle
import subprocess

import pygame

from vue.GameTitle import GameTitle
from vue.GameVue import GameVue


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

    __slots__ = ["screen", "title_screen", "parameter", "game_screen", "event"]

    def __init__(self):
        """
            Initializes the Core instance.
        """
        self.game_screen = None
        self.screen = None
        self.title_screen = None
        self.parameter = None
        self.event = pygame.event.custom_type()

        pygame.init()

        self.setup_parameter()

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
        pygame.display.set_icon(pygame.image.load("assets/icon/exodus.png"))

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

        self.parameter = dico
        self.update_screen()

    def update_screen(self):
        if self.parameter["fullscreen"]:
            flags = pygame.FULLSCREEN | pygame.SCALED
        else:
            flags = pygame.SCALED
        self.screen = pygame.display.set_mode((self.parameter["width"], self.parameter["height"]), flags)

    def default_config(self) -> dict:
        """
            Returns default configuration parameters.
        """
        return dict(version="1.0.0", fullscreen=True, width=pygame.display.get_desktop_sizes()[0][0],
                    height=pygame.display.get_desktop_sizes()[0][1])

    @staticmethod
    def game_version() -> str:
        """
            Returns the version of the game.
        """
        patch = subprocess.run(['git', 'rev-list', '--all', '--count'], capture_output=True).stdout.decode(
            'utf-8').strip()
        return "0.0." + str(patch)

    def update_parameter(self):
        """
            Updates the game parameters if necessary.
        """
        pass

    def run(self):
        """
            Starts the game execution.
        """
        self.title_screen = GameTitle(self)
        self.title_screen.setup()
        self.title_screen.run()
        del self.title_screen
        for event in pygame.event.get(self.event):
            if event.dict.get("scene") == "game":
                self.start_game()

    def start_game(self):
        self.game_screen = GameVue(self)
        # TODO : self.game_screen.setup()
        self.game_screen.run()
        del self.game_screen
        #TODO : self.run()
