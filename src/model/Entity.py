class Entity:
    __slots__ = ["health", "ressources"]

    def __init__(self, health, ressources) -> None:
        self.health = health
        self.ressources = ressources