import pygame

from vue.Scene import Scene
from vue.Button import Button

class ControlScene(Scene):
    def __init__(self, core, parent_render):
        super().__init__(core)
        self.parent_render = parent_render
        self.opacity = pygame.Surface(
            (self.screen.get_width(), self.screen.get_height())
        )
        self.opacity.set_alpha(160)
        self.scale = 0.0

        button_width = self.screen.get_width() * 0.156
        button_height = self.screen.get_height() * 0.062
        font_size = int(self.screen.get_height() * 0.065)
        self.font_size = int(self.screen.get_height() * 0.030)

        text = [
            "Le but du jeu est d'agrandir le plus votre colonie spatiale en construisant de nouveaux batiments",
            "et en recuperant des ressources.",
            "Pour vous aider, vous avez des colons que vous pouvez assigner a differentes taches",
            "comme la construction de batiments, la recolte de ressources ou le combat.",
            "Pour selectionner un colon, vous pouvez cliquer sur lui ou alors en selectionner plusieurs en",
            "utilisant le clic gauche. Une fois selectionnes, vous pouvez cliquer sur une ressource ou un batiment",
            "pour les envoyer la-bas. Dans le cas d'une ressource, le colon fera des aller-retours avec le batiment",
            "le plus proche pour les deposer. Vous pouvez annuler une selection en appuyant sur echap.",
            "Les batiments, que vous pouvez construire avec le bouton \"Batiment\", ont un cout en ressources.",
            "Le batiment doit etre construit par un ou plusieurs colons. Les batiments contiennent des ameliorations",
            "qui permettent de d'ameliorer la production de ressources ou d'ameliorer sa colonie.",
            "Pour se deplacer sur la carte, il faut utiliser le clic droit. La boussole vous indique la direction de",
            "votre colonie. Vous pouvez aussi retourner a la base en cliquant sur le bouton \"Base\".",
        ]

        font = pygame.font.Font("assets/font/Junter.otf", self.font_size)
        self.rendered_text = []
        for line in text:
            self.rendered_text.append(font.render(line, True, (255, 255, 255)))

        self.apply_button = Button(
            "Ok",
            self.screen.get_width() / 2 - button_width / 2,
            self.screen.get_height() * 0.9,
            button_width,
            button_height,
            (0, 255, 0),
            "assets/font/Space-Laser-BF65f80ab15c082.otf",
            font_size,
        )

    def handle_events(self, event: pygame.event.Event):
        if self.apply_button.is_clicked(event):
            pygame.event.post(pygame.event.Event(self.event, {"scene": "title"}))
            self.running = False
        elif event.type == pygame.MOUSEMOTION:
            if self.apply_button.is_hovered(event):
                self.apply_button.color = (0, 255, 0)
            else:
                self.apply_button.color = (0, 200, 0)
        if event.type == pygame.QUIT:
            pygame.event.post(pygame.event.Event(self.event, {"scene": "quit"}))

    def update(self):
        if self.scale < 0.99:
            self.scale += 0.02

    def render(self):
        self.parent_render()

        self.screen.blit(self.opacity, (0, 0))

        i = 0
        for line in self.rendered_text:
            self.screen.blit(
                line,
                (
                    50,
                    50 + (self.font_size + 18) * i,
                ),
            )
            i += 1

        self.apply_button.render(self.screen)

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