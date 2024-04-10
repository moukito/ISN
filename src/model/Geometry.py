class Point:
    __slots__ = ["x", "y"]

    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Point(self.x * scalar, self.y * scalar)
    
    def __div__(self, scalar):
        return Point(self.x / scalar, self.y / scalar)
    
    def __floordiv__(self, scalar):
        return Point(self.x // scalar, self.y // scalar)
    
    def __mod__(self, scalar):
        return Point(self.x % scalar, self.y % scalar)

    def __radd__(self, other):
        self.x += other.x
        self.y += other.y
    
    def __rsub__(self, other):
        self.x -= other.x
        self.y -= other.y

    def __rmul__(self, scalar):
        self.x *= scalar
        self.y *= scalar
    
    def __rdiv__(self, scalar):
        self.x /= scalar
        self.y /= scalar
    
    def __rfloordiv__(self, scalar):
        self.x //= scalar
        self.y //= scalar
    
    def __rmod__(self, scalar):
        self.x %= scalar
        self.y %= scalar

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))

    def opposite(self):
        self.x = -self.x
        self.y = -self.y

    def invert(self):
        tmp = self.x
        self.x = self.y
        self.y = tmp

    def origin():
        return Point(0, 0)

class Rectangle:
    __slots__ = ["x1", "y1", "x2", "y2"]

    def __init__(self, x1, y1, x2, y2) -> None:
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2

    @classmethod
    def fromPoints(p1, p2):
        return Rectangle(p1.x, p1.y, p2.x, p2.y)
    
    
    def containsPoint(self, point):
        return (self.x1 <= point.x and point.x <= self.x2 and
                self.y1 <= point.y and point.y <= self.y2)
    
    def containsCoords(self, x, y):
        return (self.x1 <= x and x <= self.x2 and
                self.y1 <= y and y <= self.y2)

    def overlap(self, other):
        return self.containsCoords(other.x1, other.y1) or self.containsCoords(other.x2, other.y2)
    
    def toPointList(self):
        points = []
        for y in range(self.y1, self.y2 + 1):
            for x in range(self.y1, self.y2 + 1):
                points.append(Point(x, y))
        return points
    
class Polygon:
    __slots__ = ["points"]

    def __init__(self, points) -> None:
        self.points = points

    def contains(self, point):
        length = len(self.points)
        intersections = 0

        dx2 = point[0] - self.points[0][0]
        dy2 = point[1] - self.points[0][1]
        i = 1

        contained = False

        while i < length and not contained:
            dx  = dx2
            dy  = dy2
            dx2 = point[0] - self.points[i][0]
            dy2 = point[1] - self.points[i][1]

            f = (dx - dx2) * dy - dx * (dy - dy2)
            if f == 0.0 and dx * dx2 <= 0:# and dy * dy2 <= 0:
                contained = True
            elif (dy>=0 and dy2<0) or (dy2>=0 and dy<0):
                if f > 0:
                    intersections += 1
                elif f < 0:
                    intersections -= 1

            i += 1

        return intersections != 0 or contained