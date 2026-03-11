import math

NEV = "3D Kocka"
TIPUS = "3D"
LEIRAS = """<b>Használati útmutató:</b><br>
<ul>
<li><b>Első kattintás:</b> Hova rajzolja az alakzat közepét?</li>
<li><b>Második kattintás:</b> Forgatás beállítása (X, Y dőlésszög).</li>
</ul>
<i>Ha nem kattintasz, az alakzat a rács közepén, alapértelmezett szögben jelenik meg.</i>"""


def futtat(grid_w, grid_h, p1, p2):
    nodes = [[-1, -1, -1], [-1, -1, 1], [-1, 1, -1], [-1, 1, 1], [1, -1, -1], [1, -1, 1], [1, 1, -1], [1, 1, 1]]
    edges = [(0, 1), (1, 3), (3, 2), (2, 0), (4, 5), (5, 7), (7, 6), (6, 4), (0, 4), (1, 5), (2, 6), (3, 7)]

    # 1. Opcionális középpont
    center_x, center_y = p1 if p1 != (0, 0) else (grid_w // 2, grid_h // 2)

    # 2. Opcionális forgatás
    if p2 != (0, 0):
        ax = (p2[1] / grid_h) * 6.28
        ay = (p2[0] / grid_w) * 6.28
    else:
        ax, ay = 0.6, 0.5  # Alap forgatás

    def project(node):
        x, y, z = node
        nx = x * math.cos(ay) + z * math.sin(ay)
        nz = -x * math.sin(ay) + z * math.cos(ay)
        ny = y * math.cos(ax) - nz * math.sin(ax)
        nz = y * math.sin(ax) + nz * math.cos(ax)

        factor = 2.0 / (nz + 6)
        scale = min(grid_w, grid_h) * 0.4
        return int(nx * factor * scale + center_x), int(ny * factor * scale + center_y)

    for edge in edges:
        x0, y0 = project(nodes[edge[0]])
        x1, y1 = project(nodes[edge[1]])
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            if 0 <= x0 < grid_w and 0 <= y0 < grid_h: yield x0, y0, (255, 100, 0)
            if x0 == x1 and y0 == y1: break
            e2 = 2 * err
            if e2 >= dy: err += dy; x0 += sx
            if e2 <= dx: err += dx; y0 += sy