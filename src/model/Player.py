from model.Ressource import RessourceType
from model.Upgrades import Upgrades

class Player:
    __slots__ = ["pid", "ressources", "ressource_update_callback", "upgrades"]

    PID = 0

    def __init__(self, ressource_update_callback) -> None:
        Player.PID += 1
        self.pid = Player.PID 
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
        self.upgrades = Upgrades()

    def add_ressource(self, ressource_type, quantity):
        old_ressource = self.ressources[ressource_type]
        self.ressources[ressource_type] += quantity
        if int(old_ressource) < int(old_ressource + quantity):
            self.ressource_update_callback()

    def get_ressource(self, ressource_type):
        return self.ressources.get(ressource_type, 0)