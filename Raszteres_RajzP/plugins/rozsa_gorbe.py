import math

NEV = "Parametrikus Rózsa"
TIPUS = "2D"
LEIRAS = """<b>Használati útmutató:</b><br>
Egy lenyűgöző geometriai <i>Maurer Rózsa</i> görbe.<br>
<ul>
<li><b>Első kattintás:</b> A rózsa középpontja.</li>
<li><b>Második kattintás:</b> A kattintás X és Y koordinátái megváltoztatják a szirmok számát és sűrűségét! Játssz vele!</li>
</ul>"""

PIXELS = {}


def futtat(grid_w, grid_h, p1, p2):
    cx, cy = p1 if p1 != (0, 0) else (grid_w // 2, grid_h // 2)

    # A szirom struktúráját a második kattintás koordinátáiból generáljuk
    if p2 != (0, 0):
        r = int(math.hypot(p2[0] - cx, p2[1] - cy))
        n = max(1, p2[0] % 10)  # Szirmok alapszáma
        d = max(1, p2[1] % 30)  # Fok eltolás
    else:
        r = min(grid_w, grid_h) // 2 - 2
        n = 6
        d = 71

    prev_x, prev_y = None, None
    for i in range(361):  # 0-tól 360 fokig körbeérünk
        k = i * d * math.pi / 180.0
        rad = r * math.sin(n * k)
        x = int(cx + rad * math.cos(k))
        y = int(cy + rad * math.sin(k))

        if prev_x is not None:
            # Bresenham-mal összekötjük az aktuális pontot az előzővel
            dx, dy = abs(x - prev_x), -abs(y - prev_y)
            sx, sy = (1 if prev_x < x else -1), (1 if prev_y < y else -1)
            err = dx + dy
            px, py = prev_x, prev_y
            while True:
                if 0 <= px < grid_w and 0 <= py < grid_h:
                    yield px, py, (255, 105, 180)  # Élénk rózsaszín (Hot Pink)
                if px == x and py == y: break
                e2 = 2 * err
                if e2 >= dy: err += dy; px += sx
                if e2 <= dx: err += dx; py += sy
        prev_x, prev_y = x, y