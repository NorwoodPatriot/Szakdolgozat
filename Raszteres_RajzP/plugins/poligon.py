import math

NEV = "Szabályos Hatszög"
TIPUS = "2D"
LEIRAS = """<b>Használat:</b><br>
1. Kattints a rácsra a <b>középpont</b> megadásához.<br>
2. Kattints máshova a <b>sugár</b> (méret) megadásához.<br><br>
<i>Matematika a háttérben: Trigonometria (sin, cos) segítségével számolja ki a csúcsokat.</i>"""

PIXELS = {}


def futtat(grid_w, grid_h, p1, p2):
    cx, cy = p1
    # Távolság (sugár) kiszámítása a két kattintás között
    r = math.sqrt((p2[0] - cx) ** 2 + (p2[1] - cy) ** 2)
    oldalak = 6
    szin = (200, 50, 200)

    # Először kiszámoljuk a csúcspontokat
    pontok = []
    for i in range(oldalak):
        szog = i * (2 * math.pi / oldalak)
        x = int(cx + r * math.cos(szog))
        y = int(cy + r * math.sin(szog))
        pontok.append((x, y))

    # Majd összekötjük őket a Bresenham algoritmussal (ide van ágyazva)
    for i in range(oldalak):
        x0, y0 = pontok[i]
        x1, y1 = pontok[(i + 1) % oldalak]  # Az utolsót kösse össze az elsővel

        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy

        while True:
            if 0 <= x0 < grid_w and 0 <= y0 < grid_h:
                yield x0, y0, szin
            if x0 == x1 and y0 == y1: break
            e2 = 2 * err
            if e2 >= dy: err += dy; x0 += sx
            if e2 <= dx: err += dx; y0 += sy