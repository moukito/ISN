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
    
    def __str__(self):
        return f"Point({self.x}, {self.y})"

    def opposite(self):
        self.x = -self.x
        self.y = -self.y

    def invert(self):
        tmp = self.x
        self.x = self.y
        self.y = tmp
    
    def distance(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def origin():
        return Point(0, 0)

class Rectangle:
    __slots__ = ["x1", "y1", "x2", "y2"]

    def __init__(self, x1, y1, x2, y2) -> None:
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2

    @staticmethod
    def fromPoints(p1, p2):
        x1 = p1.x
        x2 = p2.x
        y1 = p1.y
        y2 = p2.y
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        return Rectangle(x1, y1, x2, y2)
    
    def __str__(self):
        return f"Rectangle({self.x1}, {self.y1}, {self.x2}, {self.y2})"
    
    
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
    
class Circle:
    __slots__ = ["center", "radius"]

    def __init__(self, center, radius) -> None:
        self.center = center
        self.radius = radius

    def contains(self, point):
        return self.center.distance(point) <= self.radius

    def overlap(self, other):
        return self.center.distance(other.center) <= self.radius + other.radius
    
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