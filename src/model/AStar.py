from model.Geometry import Point

class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

def AStar(start, end, map):
    open_list = []
    closed_list = []

    start_node = Node(start)
    end_node = Node(end)

    open_list.append(start_node)

    while open_list:
        current_node = open_list[0]
        current_index = 0

        for index, node in enumerate(open_list):
            if node.f < current_node.f:
                current_node = node
                current_index = index

        open_list.pop(current_index)
        closed_list.append(current_node)

        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]

        neighbors = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            if map.occupied_coords.get(Point(node_position[0], node_position[1]), None):
                continue

            new_node = Node(node_position, current_node)
            neighbors.append(new_node)

        for neighbor in neighbors:
            if neighbor in closed_list:
                continue

            neighbor.g = current_node.g + 1
            neighbor.h = abs(neighbor.position[0] - end_node.position[0]) + abs(neighbor.position[1] - end_node.position[1])
            neighbor.f = neighbor.g + neighbor.h

            if neighbor in open_list:
                if neighbor.g > current_node.g:
                    continue

            open_list.append(neighbor)

    return None