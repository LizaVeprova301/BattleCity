from collections import deque

import pygame


def load_image(path, scale=None):
    img = pygame.image.load(path)
    if scale:
        img = pygame.transform.scale(img, scale)
    return img.convert_alpha()


def shortest_path(gra, start, end):
    queue = deque()
    queue.append(start)

    prev = {start: None}
    list1 = []
    for el in gra.keys():
        list1.append(el)
    for el in gra.values():
        for e in el:
            list1.append(e)

    distances = {vertex: float('inf') for vertex in list1}
    distances[start] = 0
    while queue:
        current_vertex = queue.popleft()

        if current_vertex == end:
            path = []
            while current_vertex is not None:
                path.append(current_vertex)
                current_vertex = prev[current_vertex]

            return path[::-1]

        if current_vertex in gra:
            for neighbor in gra[current_vertex]:
                if neighbor in distances and distances[neighbor] == float(
                        'inf'):
                    queue.append(neighbor)
                    distances[neighbor] = distances[current_vertex] + 1
                    prev[neighbor] = current_vertex

    return []


def make_graph_from_map(road):
    graph = {}
    for i in range(25):
        for j in range(25):
            if (i, j) not in graph:
                try:
                    if all(road[2 * i + q][2 * j + w] not in [1, 2] for q in
                           range(2) for w in range(2)):
                        graph[(i, j)] = []
                except Exception:
                    pass
            for q in range(-1, 2):
                for w in range(-1, 2):
                    try:
                        if i - q >= 0 and j - w >= 0 and \
                                all(road[2 * i - 2 * q + e][2 * j - 2 * w + r] != 1
                                    for e in range(2)
                                    for r in range(2)) and \
                                abs(q) + abs(w) != 2 and abs(q) + abs(w) != 0:
                            graph[(i, j)].append((i - q, j - w))
                    except Exception:
                        pass
    return graph
