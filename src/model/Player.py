class Player:
    __slots__ = ["ressources"]

    def __init__(self) -> None:
        self.ressources = {}

    def add_ressource(self, ressource_type, quantity):
        self.ressources[ressource_type] += quantity

    def get_ressource(self, ressource_type):
        return self.ressources.get(ressource_type, 0)