import math

NEV = "3D Drótváz Gömb"
TIPUS = "3D"
LEIRAS = """<b>Használat:</b><br>
1. Az első kattintás határozza meg, hova rajzolja a <b>középpontot</b>.<br>
2. A második kattintással beállíthatod a <b>forgatás szögét</b>.<br><br>
<i>Tipp: Állítsd a sebességet gyorsabbra (balra), mert sok pontból áll!</i>"""

PIXELS = {}


def futtat(grid_w, grid_h, p1, p2):
    center_x, center_y = p1
    ax = (p2[1] / grid_h) * 6.28 if p2 else 0.5
    ay = (p2[0] / grid_w) * 6.28 if p2 else 0.5

    latitudes = 10  # Szélességi körök
    longitudes = 15  # Hosszúsági körök
    nodes = []

    # 1. Gömb pontjainak generálása (Gömbkoordináta-rendszer)
    for i in range(latitudes + 1):
        lat = math.pi * i / latitudes
        for j in range(longitudes):
            lon = 2 * math.pi * j / longitudes
            x = math.sin(lat) * math.cos(lon)
            y = math.sin(lat) * math.sin(lon)
            z = math.cos(lat)
            nodes.append([x, y, z])

    def project(node):
        x, y, z = node
        # Forgatás
        nx = x * math.cos(ay) + z * math.sin(ay)
        nz = -x * math.sin(ay) + z * math.cos(ay)
        ny = y * math.cos(ax) - nz * math.sin(ax)
        nz = y * math.sin(ax) + nz * math.cos(ax)

        factor = 2.0 / (nz + 4)
        scale = min(grid_w, grid_h) * 0.4
        sx = int(nx * factor * scale + center_x)
        sy = int(ny * factor * scale + center_y)
        return sx, sy

    # 2. Pontok kirajzolása (Itt most nem kötözzük össze vonalakkal,
    # mert túl tömör lenne, inkább "pontfelhőként" rajzoljuk ki)
    for node in nodes:
        sx, sy = project(node)
        # Kis pöttyöt rajzolunk minden csomóponthoz
        yield sx, sy, (0, 200, 255)
        yield sx + 1, sy, (0, 200, 255)
        yield sx, sy + 1, (0, 200, 255)
        yield sx + 1, sy + 1, (0, 200, 255)