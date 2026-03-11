import random

NEV = "Sierpinski Fraktál"
TIPUS = "2D"


def futtat(grid_w, grid_h, p1, p2):
    # Három csúcspont a rács szélén
    corners = [(grid_w // 2, 0), (0, grid_h - 1), (grid_w - 1, grid_h - 1)]
    cx, cy = grid_w // 2, grid_h // 2  # Kezdőpont középen

    for _ in range(grid_w * grid_h):  # Annyi pontot rakunk, ahány cella van
        target = random.choice(corners)
        cx = (cx + target[0]) // 2
        cy = (cy + target[1]) // 2
        yield cx, cy, (255, 255, 255)  # Fehér pontok