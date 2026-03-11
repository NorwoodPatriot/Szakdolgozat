NEV = "Bresenham Vonal"
TIPUS = "2D"
LEIRAS = """<b>Használati útmutató:</b><br>
<ul>
<li><b>Első kattintás (Start):</b> A vonal kezdőpontja.</li>
<li><b>Második kattintás (Vége):</b> A vonal végpontja.</li>
</ul>
<i>Ha nem kattintasz, automatikusan húz egy átlót a bal felső sarokból a jobb alsóba.</i><br><br>
Oktatási cél: A leggyorsabb szoftveres vonalrajzoló algoritmus, lebegőpontos számítások nélkül."""

def futtat(grid_w, grid_h, p1, p2):
    # Alapértelmezés, ha nincs kattintás
    if p1 == (0, 0) and p2 == (0, 0):
        p1 = (0, 0)
        p2 = (grid_w - 1, grid_h - 1)

    x0, y0 = p1
    x1, y1 = p2
    szin = (30, 144, 255) # Acélkék

    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy

    while True:
        yield x0, y0, szin
        if x0 == x1 and y0 == y1: break
        e2 = 2 * err
        if e2 >= dy: err += dy; x0 += sx
        if e2 <= dx: err += dx; y0 += sy