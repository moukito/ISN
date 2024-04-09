import pygame
from abc import ABC, abstractmethod

class Scene(ABC):
    __slots__ = ["running"]

    def __init__(self):
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            self.decorator_handle_events()
            self.decorator_update()
            self.decorator_render()

    def decorator_handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.handle_events()

    def decorator_update(self):
        pass

    def decorator_render(self):
        pass

    @abstractmethod
    def handle_events(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self):
        pass
