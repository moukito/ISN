import pygame
import threading
from abc import ABC, abstractmethod

class Scene(ABC):
    __slots__ = ["running"]

    def __init__(self):
        self.running = False

    def run(self):
        self.running = True

        threading.Thread(target=self.event_loop)

        while self.running:
            self.decorator_update()
            self.decorator_render()

    def decorator_handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            self.handle_events(event)
        pygame.event.clear()

    def decorator_update(self):
        pass

    def decorator_render(self):
        pass

    def event_loop(self):
        while self.running:
            self.decorator_handle_events()

    @abstractmethod
    def handle_events(self, event):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self):
        pass
