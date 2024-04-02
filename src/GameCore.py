import json
import os

import pygame

from src.scene.GameTitle import GameTitle


class GameCore:
    __slots__ = ["screen", "title_screen"]

    def __init__(self, title: str, icon: str):
        pygame.init()
        self.screen = pygame.display
        self.title_screen = GameTitle()

        self.screen.set_caption(title, icon)

        self.setup_parameter()
        self.run()

    def __del__(self):
        pygame.quit()

    def setup_parameter(self):
        if not os.path.isfile("config.json"):
            with open("config.json", "w") as configFile:
                json.dump(self.default_config(), configFile)
        with open("config.json", "r") as configFile:
            dico = json.load(configFile)
        if dico["fullscreen"]:
            self.screen.set_mode((dico["width"], dico["height"]), pygame.FULLSCREEN)
        else:
            self.screen.set_mode((dico["width"], dico["height"]))

    def default_config(self) -> dict:
        return dict(fullscreen=True, width=self.screen.get_desktop_sizes()[0][0],
                    height=self.screen.get_desktop_sizes()[0][1])

    def run(self):
        self.title_screen.run()
