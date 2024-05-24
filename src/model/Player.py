from model.Ressource import RessourceType

class Player:
    __slots__ = ["ressources", "ressource_update_callback"]

    def __init__(self, ressource_update_callback) -> None:
        self.ressources = {
            RessourceType.FOOD: 200,
            RessourceType.WOOD: 150,
            RessourceType.STONE: 0,
            RessourceType.GOLD: 50, 
            RessourceType.COPPER: 0, 
            RessourceType.IRON: 0,
            RessourceType.CRYSTAL: 0,
            RessourceType.VULCAN: 0
        }
        self.ressource_update_callback = ressource_update_callback

    def add_ressource(self, ressource_type, quantity):
        old_ressource = self.ressources[ressource_type]
        self.ressources[ressource_type] += quantity
        if int(old_ressource) < int(old_ressource + quantity):
            self.ressource_update_callback()

    def get_ressource(self, ressource_type):
        return self.ressources.get(ressource_type, 0)