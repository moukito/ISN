class Player:
    __slots__ = ["ressources"]

    def __init__(self) -> None:
        self.ressources = {}

    def add_ressource(self, ressource_type, quantity):
        self.ressources[ressource_type] += quantity