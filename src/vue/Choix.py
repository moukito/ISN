class Choix:
    __slots__ = ["choix"]

    def __init__(self):
        self.choix = 1

    def __add__(self, de):
        self.choix += de
        self.check()

    def __sub__(self, de):
        self.choix -= de
        self.check()

    def check(self):
        while self.choix < 1:
            self.choix += 3
        while self.choix > 3:
            self.choix -= 3

    def get_choix(self):
        return self.choix
