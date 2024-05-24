import pygame

from vue.Button import Button

from model.Geometry import Point, Rectangle
from model.Structures import BuildingType
from model.Ressource import RessourceType

class BuildingChoice:
    __slots__ = ["building_list", "buttons", "font", "player", "screen", "screen_size", "ressource_rect_size", "width", "margin", "padding", "rect", "ressource_icons"]

    def __init__(self, player, screen, screen_size, ressource_rect_size, ressource_icons):
        self.building_list =  {
            BuildingType.FARM: ("Ferme", {RessourceType.WOOD: 50}), 
            BuildingType.PANTRY: ("Garde-Manger", {RessourceType.WOOD: 75, RessourceType.STONE: 25}),
            BuildingType.MINER_CAMP: ("Camp de Mineurs", {RessourceType.WOOD: 75, RessourceType.STONE: 25})
        }
        self.buttons = {}
        self.font = pygame.font.Font(None, 15) # TODO : change the font
        self.player = player
        self.screen = screen
        self.screen_size = screen_size
        self.ressource_rect_size = ressource_rect_size
        self.width = ressource_rect_size.x
        self.margin = 5
        self.padding = 3
        self.rect = Rectangle(0, 0, self.width, self.screen_size.y - self.ressource_rect_size.y - 20)
        self.ressource_icons = ressource_icons

        self.create_buttons()

    def create_buttons(self):
        i = 0
        for building_type, _ in self.building_list.items():
            button = Button("", self.margin + i % 2 * (140 + self.margin * 2), self.margin + (140 + self.margin * 2) * (i // 2), 140, 140, (175, 175, 175), None, 0)
            self.buttons[building_type] = button
            i += 1

    def display_building(self, building_type, building_info, position):
        self.buttons[building_type].render(self.screen)
        name = self.font.render(building_info[0], True, (0, 0, 0))
        blit_pos = position + Point(self.padding, self.padding)
        self.screen.blit(name, (blit_pos.x, blit_pos.y))
        
        # TODO : display the building image
        
        i = 0
        for ressource_type, ressource_number in building_info[1].items():
            ressource_quantity = self.font.render(str(ressource_number), True, (0, 0, 0) if self.player.get_ressource(ressource_type) >= ressource_number else (255, 50, 50))
            blit_pos = position + Point(i * 35, 50)
            self.screen.blit(ressource_quantity, (blit_pos.x, blit_pos.y))
            blit_pos = position + Point(i * 35 + 10, 50)
            self.screen.blit(self.ressource_icons[ressource_type], (blit_pos.x, blit_pos.y))
            i += 1

    def render(self):
        pygame.draw.rect(self.screen, (255, 255, 255), (self.rect.x1, self.rect.y1, self.rect.width(), self.rect.height()))
        i = 0
        for building_type, building_info in self.building_list.items():
            self.display_building(building_type, building_info, Point(self.margin + i % 2 * (140 + self.margin * 2), self.margin + (140 + self.margin * 2) * (i // 2)))
            i += 1

    def event_stream(self, event):
        result = None
        for building_type, button in self.buttons.items():
            clicked = button.is_clicked(event)
            if clicked:
                enough_ressources = True
                for ressource_type, ressource_number in self.building_list[building_type][1].items():
                    if self.player.get_ressource(ressource_type) < ressource_number:
                        enough_ressources = False
                if enough_ressources:
                    result = building_type
                
                button.color = (195, 195, 195)
            if button.is_hovered(event):
                button.color = (160, 160, 160)
            elif not clicked:
                button.color = (125, 125, 125)
        return result