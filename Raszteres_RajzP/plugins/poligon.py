import math

NEV = "Szabályos Hatszög"
TIPUS = "2D"
LEIRAS = """<b>Használati útmutató:</b><br>
<ul>
<li><b>Első kattintás:</b> A középpont megadása.</li>
<li><b>Második kattintás:</b> A sugár (méret) megadása.</li>
</ul>
<i>Ha nullázod a koordinátákat, egy automatikus méretű hatszöget tesz a rács közepére!</i>"""

PIXELS = {}


def futtat(grid_w, grid_h, p1, p2):
    # Alapértelmezett pozíció ÉS méret
    if p1 == (0, 0) and p2 == (0, 0):
        cx, cy = grid_w // 2, grid_h // 2
        r = min(grid_w, grid_h) // 3  # A rács harmada legyen a sugár
    else:
        cx, cy = p1
        r = math.sqrt((p2[0] - cx) ** 2 + (p2[1] - cy) ** 2)
        if r == 0: r = 5  # Biztonsági minimum, hogy ne legyen 0

    oldalak = 6
    szin = (200, 50, 200)

    pontok = []
    for i in range(oldalak):
        szog = i * (2 * math.pi / oldalak)
        x = int(cx + r * math.cos(szog))
        y = int(cy + r * math.sin(szog))
        pontok.append((x, y))

    for i in range(oldalak):
        x0, y0 = pontok[i]
        x1, y1 = pontok[(i + 1) % oldalak]

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

            #tesztelve