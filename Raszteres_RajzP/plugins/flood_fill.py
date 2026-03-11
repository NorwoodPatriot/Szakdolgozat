NEV = "Flood Fill (Kitöltés)"
TIPUS = "2D"
LEIRAS = """<b>Használati útmutató:</b><br>
<b style="color:red;">FONTOS:</b> Vedd ki a pipát a <i>'Törlés indítás előtt'</i> dobozból!<br>
<ul>
<li><b>Első kattintás:</b> Kattints egy zárt alakzat belsejébe a kifestéshez.</li>
<li><b>Sebesség:</b> Húzd a csúszkát balra (gyorsra), különben lassan fog végezni!</li>
</ul>"""

PIXELS = {}


def futtat(grid_w, grid_h, p1, p2):
    start_x, start_y = p1
    target_color = (100, 255, 100)  # Zöld

    def get_color(x, y):
        c = PIXELS.get((x, y))
        return (c.red(), c.green(), c.blue()) if c else None

    start_color = get_color(start_x, start_y)
    if start_color == target_color: return

    stack = [(start_x, start_y)]
    visited = set()

    while stack:
        x, y = stack.pop()
        if x < 0 or x >= grid_w or y < 0 or y >= grid_h or (x, y) in visited: continue

        if get_color(x, y) == start_color:
            visited.add((x, y))
            yield x, y, target_color
            stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])