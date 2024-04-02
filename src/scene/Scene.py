import pygame


class Scene:
    __slots__ = ["running"]

    def __init__(self):
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            self.handle_events()
            self.update()
            self.render()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    def update(self):
        pass

    def render(self):
        pass
