import json
import os
import sys

import pygame

from vue.GameTitle import GameTitle


class Core:
    __slots__ = ["screen", "title_screen"]

    def __init__(self):
        pygame.init()
        self.screen = pygame.display
        self.title_screen = GameTitle()

        self.screen.set_caption("Exodus", "../../asset/icons/exodus.png")

        self.setup_parameter()

    def __del__(self):
        pygame.quit()

    def setup_parameter(self):
        if not os.path.isfile("config.json"):
            with open("config.json", "w") as configFile:
                json.dump(self.default_config(), configFile)

        with open("config.json", "r") as configFile:
            dico = json.load(configFile)
            if dico.get("version") != self.game_version():
                self.update_parameter()

        if dico["fullscreen"]:
            self.screen.set_mode((dico["width"], dico["height"]), pygame.FULLSCREEN)
        else:
            self.screen.set_mode((dico["width"], dico["height"]))

    def default_config(self) -> dict:
        return dict(version="1.0.0", fullscreen=True, width=self.screen.get_desktop_sizes()[0][0],
                    height=self.screen.get_desktop_sizes()[0][1])

    def game_version(self):
        return "1.0.0"

    def update_parameter(self):
        pass

    def run(self):
        self.title_screen.run()
