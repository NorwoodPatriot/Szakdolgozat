NEV = "Bresenham Vonal"
TIPUS = "2D"


def futtat(width, height, p1, p2):
    x0, y0 = p1
    x1, y1 = p2

    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy

    while True:
        # Minden lépésnél átadjuk a koordinátákat a keretrendszernek
        yield x0, y0, (30, 144, 255)  # Szép acélkék szín

        if x0 == x1 and y0 == y1:
            break

        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy