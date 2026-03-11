NEV = "Flood Fill (Okos Kitöltés)"
TIPUS = "2D"

PIXELS = {}


def futtat(grid_w, grid_h, p1, p2):
    start_x, start_y = p1
    target_color = (100, 255, 100)  # Zöld festék

    def get_color(x, y):
        c = PIXELS.get((x, y))
        if c is None: return None
        return (c.red(), c.green(), c.blue())

    # Lekérjük, milyen színű pixelre kattintottál
    start_color = get_color(start_x, start_y)

    # Ha zöldre kattintasz, és zöldre akarod festeni, ne csináljon semmit
    if start_color == target_color:
        return

    stack = [(start_x, start_y)]
    visited = set()

    while stack:
        x, y = stack.pop()

        # Pályaelhagyás vagy már bejárt pixel szűrése
        if x < 0 or x >= grid_w or y < 0 or y >= grid_h or (x, y) in visited:
            continue

        # Csak akkor színezünk, ha a pixel színe egyezik a kezdő színnel
        if get_color(x, y) == start_color:
            visited.add((x, y))
            yield x, y, target_color

            # 4 irányba terjedés
            stack.append((x + 1, y))
            stack.append((x - 1, y))
            stack.append((x, y + 1))
            stack.append((x, y - 1))