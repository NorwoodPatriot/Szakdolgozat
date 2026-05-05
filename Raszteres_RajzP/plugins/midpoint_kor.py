NEV = "Midpoint Kör"
TIPUS = "2D"
LEIRAS = """<b>Használati útmutató:</b><br>
<ul>
<li><b>Első kattintás:</b> A kör középpontja.</li>
<li><b>Második kattintás:</b> Meghatározza a kör sugarát (távolság a középponttól).</li>
</ul>
<i>Ha nem kattintasz, a rács közepére rajzol egy alapértelmezett kört.</i>"""

def futtat(grid_w, grid_h, p1, p2):
    # Alapértelmezés (Középre)
    if p1 == (0, 0) and p2 == (0, 0):
        p1 = (grid_w // 2, grid_h // 2)
        p2 = (grid_w // 2 + grid_w // 4, grid_h // 2)

    x0, y0 = p1
    r = int(((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)**0.5)
    x, y = r, 0
    err = 1 - r

    def circle_points(cx, cy, px, py):
        return [(cx+px, cy+py), (cx-px, cy+py), (cx+px, cy-py), (cx-px, cy-py),
                (cx+py, cy+px), (cx-py, cy+px), (cx+py, cy-px), (cx-py, cy-px)]

    while x >= y:
        for px, py in circle_points(x0, y0, x, y):
            if 0 <= px < grid_w and 0 <= py < grid_h:
                yield px, py, (255, 50, 50)
        y += 1
        if err <= 0:
            err += 2 * y + 1
        else:
            x -= 1
            err += 2 * (y - x) + 1

#tesztelve
