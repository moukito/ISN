import os
import pygame

from vue.Scene import Scene
from vue.Button import Button
from vue.Select import Select

class SavesScene(Scene):
    def __init__(self, core, parent_render):
        super().__init__(core)
        self.parent_render = parent_render
        self.opacity = pygame.Surface(
            (self.screen.get_width(), self.screen.get_height())
        )
        self.opacity.set_alpha(160)
        self.scale = 0.0

        self.save_name = None

        saves_directory = "saves"
        saves = []
        if os.path.exists(saves_directory):
            for name in os.listdir(saves_directory):
                if os.path.isdir(os.path.join(saves_directory, name)):
                    saves.append(name)

        self.save_menu = None
        if len(saves) > 0:
            self.save_menu = Select(
                20,
                200,
                300,
                50,
                saves,
                self.save_name,
            )

        button_width = self.screen.get_width() * 0.156
        button_height = self.screen.get_height() * 0.062
        font_size = int(self.screen.get_height() * 0.065)

        self.apply_button = Button(
            "Apply",
            self.screen.get_width() * 3 / 4 - button_width / 2,
            self.screen.get_height() * 0.9,
            button_width,
            button_height,
            (0, 255, 0),
            "assets/font/Space-Laser-BF65f80ab15c082.otf",
            font_size,
        )
        self.cancel_button = Button(
            "Cancel",
            self.screen.get_width() / 4 - button_width / 2,
            self.screen.get_height() * 0.9,
            button_width,
            button_height,
            (255, 0, 0),
            "assets/font/Space-Laser-BF65f80ab15c082.otf",
            font_size,
        )

    def handle_events(self, event: pygame.event.Event):
        if self.apply_button.is_clicked(event):
            self.core.save_name = self.save_name
            pygame.event.post(pygame.event.Event(self.event, {"scene": "title"}))
            self.running = False
        elif self.cancel_button.is_clicked(event):
            pygame.event.post(pygame.event.Event(self.event, {"scene": "title"}))
            self.running = False
        elif event.type == pygame.MOUSEMOTION:
            for button in [self.apply_button, self.cancel_button]:
                if button.is_hovered(event):
                    self.change_button_color(button, True)
                else:
                    self.change_button_color(button, False)
        if self.save_menu is not None:
            self.save_menu.handle_event(event)
        if event.type == pygame.QUIT:
            pygame.event.post(pygame.event.Event(self.event, {"scene": "quit"}))

    def update(self):
        if self.scale < 0.99:
            self.scale += 0.02

        self.core.save_name = self.save_menu.get_value()

    def render(self):
        self.parent_render()

        self.screen.blit(self.opacity, (0, 0))

        if self.save_menu is not None:
            self.save_menu.render(self.screen)

        self.apply_button.render(self.screen)
        self.cancel_button.render(self.screen)

        scaled_screen = pygame.transform.scale(
            self.screen,
            (
                int(self.screen.get_width() * self.scale),
                int(self.screen.get_height() * self.scale),
            ),
        )

        self.parent_render()
        self.screen.blit(
            scaled_screen,
            (
                (self.screen.get_width() - scaled_screen.get_width()) // 2,
                (self.screen.get_height() - scaled_screen.get_height()) // 2,
            ),
        )

    @staticmethod
    def change_button_color(button, hovered):
        """
        Changes the color of the button when hovered.

        Parameters:
            button (Button): The button to change the color of.
            hovered (bool): Whether the button is hovered or not.
        """
        if hovered:
            if button.text == "Apply":
                button.color = (0, 255, 0)
            else:
                button.color = (255, 0, 0)
        else:
            if button.text == "Apply":
                button.color = (0, 200, 0)
            else:
                button.color = (200, 0, 0)