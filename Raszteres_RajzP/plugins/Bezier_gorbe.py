NEV = "Bezier Görbe"
TIPUS = "2D"

def futtat(grid_w, grid_h, p1, p2):
    p0 = p1 # Start
    p2_end = p2 # Vége
    p1_ctrl = (p2[0], p1[1]) # Kontroll pont (derékszögben)

    for i in range(101):
        t = i / 100
        # Másodfokú Bezier képlet
        x = (1-t)**2 * p0[0] + 2*(1-t)*t * p1_ctrl[0] + t**2 * p2_end[0]
        y = (1-t)**2 * p0[1] + 2*(1-t)*t * p1_ctrl[1] + t**2 * p2_end[1]
        yield int(x), int(y), (0, 255, 255)