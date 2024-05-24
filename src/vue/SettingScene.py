import pygame

from vue.Core import Core
from vue.Button import Button
from vue.Scene import Scene
from vue.Select import Select
from vue.Slider import Slider


# TODO : adjust the select and slider class to the new structure
class SettingsScene(Scene):
    """
    Represents the settings screen of the game.
    Inherits from the Scene class.

    Methods:
        __init__(screen): Initializes the SettingsScene instance with the screen.
        handle_events(): Handles events specific to the settings screen.
        update(): Updates the settings screen.
        render(): Renders the settings screen.
        increase_volume(): Increases the game volume.
        decrease_volume(): Decreases the game volume.
        change_resolution(): Changes the game resolution.
    """

    __slots__ = [
        "opacity",
        "scale",
        "volume",
        "resolution",
        "volume_slider",
        "resolution_menu",
        "apply_button",
        "cancel_button",
        "parent_render",
    ]

    def __init__(self, core: Core, parent_render: callable) -> None:
        """
        Initializes the SettingsScene instance with the screen.

        Parameters:
            core (pygame.Surface): The surface to render the settings screen on.
        """
        super().__init__(core)
        self.parent_render = parent_render
        self.opacity = pygame.Surface(
            (self.screen.get_width(), self.screen.get_height())
        )
        self.opacity.set_alpha(160)
        self.scale = 0.1

        self.volume = pygame.mixer.music.get_volume()
        self.resolution = (self.screen.get_width(), self.screen.get_height())

        self.volume_slider = Slider(20, 100, 200, 20, 0.0, 1.0, self.volume)
        self.resolution_menu = Select(
            20,
            200,
            200,
            50,
            [(800, 600), (1024, 768), (1920, 1080), (2560, 1440), (3840, 2160)],
            self.resolution,
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

    def __del__(self) -> None:
        self.fade_out()

    def handle_events(self, event: pygame.event.Event) -> None:
        """
        Handles events specific to the settings screen.
        """
        if self.apply_button.is_clicked(event):
            # Apply the settings
            self.parameter["volume"] = self.volume
            self.parameter["width"] = self.resolution[0]
            self.parameter["height"] = self.resolution[1]

            self.core.update_parameter(self.parameter)

            pygame.event.post(pygame.event.Event(self.event, {"scene": "title"}))
            self.running = False
        elif self.cancel_button.is_clicked(event):
            # Cancel the settings
            pygame.event.post(pygame.event.Event(self.event, {"scene": "title"}))
            self.running = False
        elif event.type == pygame.MOUSEMOTION:
            for button in [self.apply_button, self.cancel_button]:
                if button.is_hovered(event):
                    self.change_button_color(button, True)
                else:
                    self.change_button_color(button, False)
        self.volume_slider.handle_event(event)
        self.resolution_menu.handle_event(event)
        if event.type == pygame.QUIT:
            pygame.event.post(pygame.event.Event(self.event, {"scene": "quit"}))

    def update(self) -> None:
        """
        Updates the settings screen.
        """
        self.volume = self.volume_slider.get_value()
        pygame.mixer.music.set_volume(self.volume)

        self.resolution = self.resolution_menu.get_value()

        if self.scale < 0.9:
            self.scale += 0.1

    def render(self) -> None:
        """
        Renders the settings screen.
        """
        window = pygame.Surface(self.screen.get_width, self.screen.get_height)
        window.fill((0, 0, 0))

        self.render_parameter(window)

        scaled_screen = pygame.transform.scale(
            window,
            (
                int(self.screen.get_width() * self.scale),
                int(self.screen.get_height() * self.scale),
            ),
        )  # Scale the screen
        # TODO : refactor render and test new fade in
        self.parent_render()
        self.screen.blit(
            scaled_screen,
            (
                (self.screen.get_width() - scaled_screen.get_width()) // 2,
                (self.screen.get_height() - scaled_screen.get_height()) // 2,
            ),
        )  # Draw the scaled screen onto the original screen

    def render_parameter(self, screen: pygame.Surface) -> None:
        screen.blit(self.opacity, (0, 0))
        volume_text = pygame.font.Font(None, 36).render(
            f"Volume: {self.volume}", 1, (255, 255, 255)
        )
        self.volume_slider.render(screen)
        resolution_text = pygame.font.Font(None, 36).render(
            f"Resolution: {self.resolution}", 1, (255, 255, 255)
        )
        self.resolution_menu.render(screen)
        screen.blit(volume_text, (20, 20))
        screen.blit(resolution_text, (20, 60))
        self.apply_button.render(screen)
        self.cancel_button.render(screen)

    def fade_out(self) -> None:
        fade_surface = pygame.Surface(
            (self.screen.get_width(), self.screen.get_height())
        )  # Create a new surface
        fade_surface.fill((0, 0, 0))  # Fill the surface with black color

        for alpha in range(0, 300):
            fade_surface.set_alpha(alpha)  # Set the alpha value
            self.render()  # Render the scene
            self.screen.blit(
                fade_surface, (0, 0)
            )  # Blit the fade surface onto the screen
            pygame.display.update()  # Update the display
            pygame.time.delay(5)  # Delay to create the fade-out effect
        # TODO : test fade out

    @staticmethod
    def change_button_color(button: Button, hovered: bool) -> None:
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
