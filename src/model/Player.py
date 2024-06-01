from model.Ressource import RessourceType

class Player:
    __slots__ = ["ressources", "ressource_update_callback"]

    def __init__(self, ressource_update_callback) -> None:
        delta = 0.05 # Add a small delta to remove floating point errors with ressource gathering
        self.ressources = {
            RessourceType.FOOD: 200 + delta,
            RessourceType.WOOD: 150 + delta,
            RessourceType.STONE: delta,
            RessourceType.GOLD: delta, 
            RessourceType.COPPER: delta,
            RessourceType.IRON: delta,
            RessourceType.CRYSTAL: delta,
            RessourceType.VULCAN: delta
        }
        self.ressource_update_callback = ressource_update_callback

    def add_ressource(self, ressource_type, quantity):
        old_ressource = self.ressources[ressource_type]
        self.ressources[ressource_type] += quantity
        if int(old_ressource) < int(old_ressource + quantity):
            self.ressource_update_callback()

    def get_ressource(self, ressource_type):
        return self.ressources.get(ressource_type, 0)