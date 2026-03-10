NEV = "Midpoint Kör"
TIPUS = "2D"


def futtat(grid_w, grid_h, p1, p2):
    x0, y0 = p1
    # Sugár kiszámítása a két pont távolságából
    r = int(((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5)

    x = r
    y = 0
    err = 1 - r

    def circle_points(cx, cy, x, y):
        # A kör nyolcadolós szimmetriája miatt 8 pontot adunk vissza egyszerre
        return [
            (cx + x, cy + y), (cx - x, cy + y), (cx + x, cy - y), (cx - x, cy - y),
            (cx + y, cy + x), (cx - y, cy + x), (cx + y, cy - x), (cx - y, cy - x)
        ]

    while x >= y:
        for px, py in circle_points(x0, y0, x, y):
            if 0 <= px < grid_w and 0 <= py < grid_h:
                yield px, py, (255, 0, 255)  # Lila

        y += 1
        if err <= 0:
            err += 2 * y + 1
        else:
            x -= 1
            err += 2 * (y - x) + 1