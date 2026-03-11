NEV = "Bézier Görbe (Másodfokú)"
TIPUS = "2D"
LEIRAS = """<b>Használati útmutató:</b><br>
<ul>
<li><b>Első kattintás (Start):</b> A görbe kezdőpontja.</li>
<li><b>Második kattintás (Vége):</b> A görbe végpontja.</li>
</ul>
<i>Ha nem kattintasz, a rács közepére rajzol egy alapértelmezett ívet. A program automatikusan generál egy kontrollpontot a megfelelő görbülethez.</i>"""

PIXELS = {}


def futtat(grid_w, grid_h, p1, p2):
    # Alapértelmezett, ha nincs kattintás
    if p1 == (0, 0) and p2 == (0, 0):
        p0 = (grid_w // 4, grid_h // 2)
        p2_end = (3 * grid_w // 4, grid_h // 2)
        p1_ctrl = (grid_w // 2, grid_h // 4)  # Felfelé ível
    else:
        p0 = p1
        p2_end = p2
        # Matematika a görbülethez: A két pont közötti távolságra merőlegesen eltoljuk a kontrollpontot
        dx, dy = p2_end[0] - p0[0], p2_end[1] - p0[1]
        p1_ctrl = (p0[0] + dx // 2 - dy // 2, p0[1] + dy // 2 + dx // 2)

    for i in range(101):
        t = i / 100.0
        # Másodfokú Bézier formula
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1_ctrl[0] + t ** 2 * p2_end[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1_ctrl[1] + t ** 2 * p2_end[1]

        if 0 <= int(x) < grid_w and 0 <= int(y) < grid_h:
            yield int(x), int(y), (0, 255, 255)  # Ciánkék