from model.Ressource import RessourceType

class Player:
    __slots__ = ["ressources"]

    def __init__(self) -> None:
        self.ressources = {
            RessourceType.FOOD: 0,
            RessourceType.WOOD: 0,
            RessourceType.STONE: 0,
            RessourceType.GOLD: 0, 
            RessourceType.COPPER: 0, 
            RessourceType.IRON: 0,
            RessourceType.CRYSTAL: 0,
            RessourceType.VULCAN: 0
        }

    def add_ressource(self, ressource_type, quantity):
        self.ressources[ressource_type] += quantity

    def get_ressource(self, ressource_type):
        return self.ressources.get(ressource_type, 0)