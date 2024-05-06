import pygame

from src.vue.Choice import Choice
from src.vue.Scene import Scene
from src.vue.SettingScene import SettingsScene


class GameTitle(Scene):
    """
        Represents the title screen of the game.
        Inherits from the Scene class.

        Methods:
            __init__(screen): Initializes the GameTitle instance with the screen.
            handle_events(): Handles events specific to the title screen.
            update(): Updates the title screen.
            render(): Renders the title screen.
    """

    __slots__ = ["bg", "choice", "options", "font"]

    def __init__(self, screen: pygame.Surface):
        """
            Initializes the GameTitle instance with the screen.

            Parameters:
                screen (pygame.Surface): The surface to render the title screen on.
        """
        super().__init__(screen)
        self.bg = pygame.transform.smoothscale(pygame.image.load("asset/background.jpg"),
                                               (self.screen.get_width(), self.screen.get_height()))
        pygame.mixer.music.load("asset/music/titleScreen.mp3")
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play()

        self.choice = Choice()
        self.options = ["jouer", "option", "quitter"]
        font_size = int(self.screen.get_height() * 0.065)
        self.font = pygame.font.Font("asset/font/Space-Laser-BF65f80ab15c082.otf", font_size)

        self.run()

    def __del__(self):
        pygame.mixer.music.stop()

    def handle_events(self, event: pygame.event.Event):
        """
            Handles events specific to the title screen.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif event.key == pygame.K_UP:
                self.choice -= 1
            elif event.key == pygame.K_DOWN:
                self.choice += 1
            elif event.key == pygame.K_RETURN:
                choice = self.choice.get_choice()
                if choice == 1:
                    pass
                elif choice == 2:
                    settings_scene = SettingsScene(self.screen)  # Create and run the settings scene
                    settings_scene.run()
                elif choice == 3:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self):
        """
            Updates the title screen.
        """
        pass

    def render(self):
        """
        Renders the title screen.

        This method is responsible for drawing the title screen on the pygame surface. It first draws the background image
        onto the screen. Then, it iterates over the list of options and renders each one as a text object on the screen.

        The text is centered horizontally on the screen. The vertical position of the text is calculated as 80% of the
        screen height plus an offset based on the index of the option in the list, which creates a vertical list of options.

        The color of the text is determined by whether the current option is the selected choice. If it is, the text is
        rendered in red. Otherwise, it is rendered in white.
        """
        self.screen.blit(self.bg, (0, 0))  # Draw the background image onto the screen

        choice = self.choice.get_choice()
        for i, option in enumerate(self.options):  # Iterate over the list of options
            if choice == i + 1:  # Check if the current option is the selected choice
                color = (196, 158, 33)  # If it is, set the color to yellow
            else:
                color = (1, 6, 138)  # If it's not, set the color to blue
            text = self.font.render(option, 1, color)  # Render the option as a text object with the determined color

            # Calculate the position of the text
            text_width, text_height = text.get_size()  # Get the size of the text object
            x = (self.screen.get_width() - text_width) // 2  # Calculate the horizontal position (centered)
            y = int(
                self.screen.get_height() * 0.65) + i * 150  # Calculate the vertical position (80% from the top plus an offset)
            position = (x, y)  # Create a tuple for the position

            self.screen.blit(text, position)  # Draw the text object onto the screen at the calculated position

            # Draw a triangle around the current choice
            if choice == i + 1:
                offset = 0.8 * text_height / 2
                x -= 20
                points = [(x - offset, y + offset * 2), (x - offset, y), (x, y + offset)]
                pygame.draw.polygon(self.screen, color, points)
                x += 40 + text_width
                points = [(x + offset, y + offset * 2), (x + offset, y), (x, y + offset)]
                pygame.draw.polygon(self.screen, color, points)
