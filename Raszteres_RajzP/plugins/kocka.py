import math

NEV = "Kocka (Kattintásra)"
TIPUS = "3D"


def futtat(grid_w, grid_h, p1, p2):
    nodes = [[-1, -1, -1], [-1, -1, 1], [-1, 1, -1], [-1, 1, 1], [1, -1, -1], [1, -1, 1], [1, 1, -1], [1, 1, 1]]
    edges = [(0, 1), (1, 3), (3, 2), (2, 0), (4, 5), (5, 7), (7, 6), (6, 4), (0, 4), (1, 5), (2, 6), (3, 7)]

    # 1. A kattintás adja meg a KÖZÉPPONTOT
    center_x, center_y = p1

    # 2. A második kattintás adja a forgatást (ha van)
    ax = (p2[1] / grid_h) * 6.28 if p2 else 0.6
    ay = (p2[0] / grid_w) * 6.28 if p2 else 0.5

    def project(node):
        x, y, z = node
        nx = x * math.cos(ay) + z * math.sin(ay)
        nz = -x * math.sin(ay) + z * math.cos(ay)
        ny = y * math.cos(ax) - nz * math.sin(ax)
        nz = y * math.sin(ax) + nz * math.cos(ax)

        factor = 2.0 / (nz + 6)

        # 3. Skálázás és Eltolás a kattintott pontra
        scale = min(grid_w, grid_h) * 0.4
        screen_x = int(nx * factor * scale + center_x)
        screen_y = int(ny * factor * scale + center_y)
        return screen_x, screen_y

    for edge in edges:
        x0, y0 = project(nodes[edge[0]])
        x1, y1 = project(nodes[edge[1]])

        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy

        while True:
            # Csak azt rajzoljuk ki, ami nem lóg le a rácsról
            if 0 <= x0 < grid_w and 0 <= y0 < grid_h:
                yield x0, y0, (255, 100, 0)
            if x0 == x1 and y0 == y1: break
            e2 = 2 * err
            if e2 >= dy: err += dy; x0 += sx
            if e2 <= dx: err += dx; y0 += sy