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

        if current_node.position == end_node.position:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]

        neighbors = []
        for new_position in [Point(0, -1), Point(0, 1), Point(-1, 0), Point(1, 0), Point(-1, -1), Point(-1, 1), Point(1, -1), Point(1, 1)]:
            node_position = current_node.position + new_position

            # TODO : When we want the obstacles (structures) to be taken into account
            #if map.occupied_coords.get(node_position, None) is not None:
            #    continue

            new_node = Node(node_position, current_node)
            neighbors.append(new_node)

        for neighbor in neighbors:
            if neighbor in closed_list:
                continue

            neighbor.g = current_node.g + 1
            neighbor.h = abs(neighbor.position.x - end_node.position.x) + abs(neighbor.position.y - end_node.position.y)
            neighbor.f = neighbor.g + neighbor.h

            if neighbor in open_list:
                if neighbor.g > current_node.g:
                    continue

            open_list.append(neighbor)

    return None