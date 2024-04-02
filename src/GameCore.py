import json
import os
import sys

import pygame

from src.scene.GameTitle import GameTitle


class GameCore:
    __slots__ = ['screen', 'title_screen']

    def __init__(self, title: str, icon: str):
        self.title_screen = None
        pygame.init()
        pygame.display.set_caption(title, icon)

        self.setupParameter()

    def __del__(self):
        pygame.quit()
        sys.exit()

    def setupParameter(self):
        if not os.path.isfile("config.json"):
            with open("config.json", "w") as configFile:
                json.dump(self.defaultConfig(), configFile)
        with open("config.json", "r") as configFile:
            dico = json.load(configFile)
        if dico["fullscreen"]:
            
        else:
            pygame.display.set_mode()

    def defaultConfig(self) -> dict:
        return dict(fullscreen=True, width=pygame.display.get_surface().get_width(),
                    height=pygame.display.get_surface().get_height())

    def run(self):
        self.title_screen = GameTitle()
