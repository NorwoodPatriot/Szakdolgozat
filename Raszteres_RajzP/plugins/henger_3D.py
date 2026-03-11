import math

NEV = "3D Henger (Cylinder)"
TIPUS = "3D"
LEIRAS = """<b>Használati útmutató:</b><br>
<ul>
<li><b>Első kattintás:</b> A henger pozíciója a rácson.</li>
<li><b>Második kattintás:</b> A forgatás szöge a 3D térben.</li>
</ul>
<i>Oktatási tipp: Figyeld meg, hogyan torzulnak a körök ellipszissé a 3D perspektíva miatt!</i>"""

PIXELS = {}


def futtat(grid_w, grid_h, p1, p2):
    center_x, center_y = p1 if p1 != (0, 0) else (grid_w // 2, grid_h // 2)

    if p2 != (0, 0):
        ax = (p2[1] / grid_h) * 6.28
        ay = (p2[0] / grid_w) * 6.28
    else:
        ax, ay = 0.5, 0.4

    szegmensek = 16  # Hány oldalú legyen a henger
    nodes = []
    edges = []

    # 1. Pontok generálása (Felső és Alsó körlap)
    for i in range(szegmensek):
        szog = 2 * math.pi * i / szegmensek
        x = math.cos(szog)
        z = math.sin(szog)
        nodes.append([x, 1.0, z])  # Felső pont
        nodes.append([x, -1.0, z])  # Alsó pont (pontosan alatta)

    # 2. Élek generálása
    for i in range(szegmensek):
        idx_top = i * 2
        idx_bottom = i * 2 + 1
        idx_next_top = ((i + 1) % szegmensek) * 2
        idx_next_bottom = ((i + 1) % szegmensek) * 2 + 1

        edges.append((idx_top, idx_bottom))  # Függőleges vonalak
        edges.append((idx_top, idx_next_top))  # Felső kör összekötése
        edges.append((idx_bottom, idx_next_bottom))  # Alsó kör összekötése

    def project(node):
        x, y, z = node
        nx = x * math.cos(ay) + z * math.sin(ay)
        nz = -x * math.sin(ay) + z * math.cos(ay)
        ny = y * math.cos(ax) - nz * math.sin(ax)
        nz = y * math.sin(ax) + nz * math.cos(ax)

        factor = 2.0 / (nz + 6)
        scale = min(grid_w, grid_h) * 0.4
        return int(nx * factor * scale + center_x), int(ny * factor * scale + center_y)

    # 3. Kirajzolás Bresenham-mal
    for edge in edges:
        x0, y0 = project(nodes[edge[0]])
        x1, y1 = project(nodes[edge[1]])
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            if 0 <= x0 < grid_w and 0 <= y0 < grid_h: yield x0, y0, (50, 205, 50)  # Lime zöld
            if x0 == x1 and y0 == y1: break
            e2 = 2 * err
            if e2 >= dy: err += dy; x0 += sx
            if e2 <= dx: err += dx; y0 += sy