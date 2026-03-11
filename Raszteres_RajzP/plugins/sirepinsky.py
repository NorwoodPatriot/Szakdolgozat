import random

NEV = "Sierpinski Fraktál"
TIPUS = "2D"
LEIRAS = """<b>Használati útmutató:</b><br>
<ul>
<li><b>Első kattintás:</b> A fraktál középpontja.</li>
<li><b>Második kattintás:</b> A méret beállítása (távolság a középponttól).</li>
</ul>
<i>Tipp: Húzd a sebességcsúszkát teljesen balra (gyorsra), mert több ezer pontból épül fel a Káosz-játék algoritmussal! Ha nem kattintasz, kitölti a rácsot.</i>"""

PIXELS = {}


def futtat(grid_w, grid_h, p1, p2):
    if p1 == (0, 0) and p2 == (0, 0):
        cx, cy = grid_w // 2, grid_h // 2
        size = min(grid_w, grid_h) // 2 - 2
    else:
        cx, cy = p1
        if p2 != (0, 0):
            size = int(((p2[0] - cx) ** 2 + (p2[1] - cy) ** 2) ** 0.5)
        else:
            size = min(grid_w, grid_h) // 4

    # A háromszög csúcsai
    corners = [
        (cx, cy - size),
        (cx - size, cy + size),
        (cx + size, cy + size)
    ]

    curr_x, curr_y = cx, cy
    limit = grid_w * grid_h  # Max iteráció

    for _ in range(limit):
        tx, ty = random.choice(corners)
        curr_x = (curr_x + tx) // 2
        curr_y = (curr_y + ty) // 2

        if 0 <= curr_x < grid_w and 0 <= curr_y < grid_h:
            yield curr_x, curr_y, (255, 255, 255)  # Fehér pontok