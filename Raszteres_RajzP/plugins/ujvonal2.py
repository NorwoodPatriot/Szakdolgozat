NEV = "ujvonal2"
TIPUS = "2D"
LEIRAS = "asd"

def futtat(res_x, res_y, p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    
    # --- ALGORITMUS LOGIKÁJA IDE JÖN ---
    
    yield (x1, y1, (255, 255, 0)) # Sárga pont
    yield (x2, y2, (255, 100, 0)) # Narancs pont
